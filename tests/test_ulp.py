"""Offline security and compatibility tests; no dependency on proprietary agent binaries."""
import importlib.util
import json
from datetime import date
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / 'scripts' / 'ulp.py'
spec = importlib.util.spec_from_file_location('ulp', CLI)
ulp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ulp)


class LocalCLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'proj'
        self.project.mkdir()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                              capture_output=True, text=True, timeout=20)

    def fixture_profile(self):
        obj = ulp.blank_profile()
        obj['owner_attestation'] = {'confirmed': True, 'role': 'owner', 'confirmed_on': date.today().isoformat()}
        obj['entity'] = {'legal_name': 'Example Organization', 'country': 'Testland',
                         'privacy_contact': 'privacy@example.invalid', 'role': 'controller'}
        obj['project'] = {'name': 'Example App', 'description': 'Internal demonstrator',
                          'business_model': 'demo', 'audience': 'invited testers',
                          'languages': ['en'], 'service_countries': ['Testland']}
        obj['legal_sources'] = [{'jurisdiction': 'Testland', 'authority': 'Fictitious Official Authority',
                                 'title': 'Synthetic law for CLI structural unit test',
                                 'url': 'https://example.invalid/law', 'section': '1',
                                 'checked_on': date.today().isoformat(), 'applies_to': 'test flow',
                                 'verified_from_official_site': True}]
        obj['processing'] = [{'purpose': 'demonstration account', 'legal_basis': 'confirmed in test only',
                              'retention': 'test lifespan', 'source_of_data': 'test input',
                              'deletion_process': 'test cleanup', 'data_categories': ['test label'],
                              'recipients': [], 'transfer_countries': [], 'verified': True}]
        obj['terms'] = {'service_scope': 'Test only', 'eligibility': 'Testers',
                        'user_obligations': 'Use test data', 'termination': 'Test ends', 'payment_terms': ''}
        obj['cookies'] = [{'name':'sample', 'provider':'example', 'purpose':'test',
                           'category':'essential', 'duration':'session', 'control':'test', 'verified':True}]
        return obj

    def test_bundle_validation(self):
        r=self.run_cli('verify-bundle','--root',ROOT)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertIn('"pass"',r.stdout)

    def test_apache_license_metadata_and_full_text(self):
        license_text=(ROOT/'LICENSE').read_text(encoding='utf-8')
        skill=(ROOT/'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Apache License',license_text)
        self.assertIn('Version 2.0, January 2004',license_text)
        self.assertIn('END OF TERMS AND CONDITIONS',license_text)
        self.assertIn('license: Apache-2.0',skill)

    def test_scan_only_candidates_and_redacts_values(self):
        (self.project/'app.ts').write_text("const email = 'person@real.example';\nlocalStorage.setItem('secret', 'private-value');\n")
        (self.project/'.env').write_text('SENSITIVE_TOKEN=never-display')
        (self.project/'credential-file.ts').write_text('google-analytics.com SECRET-VALUE')
        r=self.run_cli('scan','--project',self.project)
        self.assertEqual(r.returncode,0,r.stderr)
        data=json.loads(r.stdout)
        self.assertGreater(data['signals_count'],0)
        self.assertEqual(data['mode'],'read-only-candidate-scan')
        self.assertNotIn('never-display',r.stdout)
        self.assertNotIn('private-value',r.stdout)
        self.assertNotIn('person@real.example',r.stdout)
        self.assertNotIn('credential-file',r.stdout)
        self.assertEqual(list(self.project.iterdir()).__len__(),3)

    def test_scan_refuses_write_without_approval(self):
        r=self.run_cli('scan','--project',self.project,'--out','.legal-privacy/work/scan.json')
        self.assertNotEqual(r.returncode,0)
        self.assertFalse((self.project/'.legal-privacy').exists())

    def test_output_cannot_escape_and_no_overwrite(self):
        a=self.run_cli('scan','--project',self.project,'--out','../../outside.json','--approve-workfiles')
        self.assertNotEqual(a.returncode,0)
        b=self.run_cli('scan','--project',self.project,'--out','.legal-privacy/work/report.json','--approve-workfiles')
        self.assertEqual(b.returncode,0,b.stderr)
        c=self.run_cli('scan','--project',self.project,'--out','.legal-privacy/work/report.json','--approve-workfiles')
        self.assertNotEqual(c.returncode,0)

    def test_blank_profile_stops_draft(self):
        a=self.run_cli('init-profile','--project',self.project,'--approve-workfiles')
        self.assertEqual(a.returncode,0,a.stderr)
        path=self.project/'.legal-privacy/work/profile.json'
        r=self.run_cli('draft','--project',self.project,'--profile',path,
                       '--types','privacy','--approve-workfiles')
        self.assertEqual(r.returncode,2)
        self.assertFalse((self.project/'.legal-privacy/work/drafts').exists())

    def test_privacy_draft_requires_scope_and_is_nonpublic(self):
        obj=self.fixture_profile()
        profile=self.project/'profile.json'
        profile.write_text(json.dumps(obj))
        a=self.run_cli('draft','--project',self.project,'--profile',profile,'--types','privacy')
        self.assertNotEqual(a.returncode,0)
        b=self.run_cli('draft','--project',self.project,'--profile',profile,'--types','privacy','--approve-workfiles')
        self.assertEqual(b.returncode,0,b.stderr)
        docs=list((self.project/'.legal-privacy/work/drafts').glob('*.md'))
        self.assertEqual(len(docs),1)
        self.assertIn('NOT APPROVED FOR PUBLICATION',docs[0].read_text())
        self.assertIn('Example Organization',docs[0].read_text())
        self.assertFalse((self.project/'public').exists())

    def test_future_dated_legal_source_is_blocked(self):
        obj=self.fixture_profile()
        obj['legal_sources'][0]['checked_on']='2999-01-01'
        self.assertTrue(any('reverified' in e for e in ulp.validate_profile(obj,['privacy'])))

    def test_specialist_review_gate(self):
        obj=self.fixture_profile()
        obj['review']={'specialist_required':True,'specialist_review_confirmed':False}
        p=self.project/'p.json'
        p.write_text(json.dumps(obj))
        r=self.run_cli('draft','--project',self.project,'--profile',p,'--types','privacy','--approve-workfiles')
        self.assertEqual(r.returncode,2)

    def test_install_all_agent_project_paths_nonoverwriting(self):
        for agent, rel in [('antigravity','.agents/skills'),('claude','.claude/skills'),('codex','.agents/skills')]:
            project=self.project/agent
            project.mkdir()
            a=self.run_cli('install','--agent',agent,'--scope','project','--project',project,'--approve-install')
            self.assertEqual(a.returncode,0,a.stderr)
            dest=project/rel/'universal-legal-privacy'
            self.assertTrue((dest/'SKILL.md').exists())
            self.assertTrue((dest/'LICENSE').exists())
            self.assertTrue((dest/'scripts/ulp.py').exists())
            b=self.run_cli('install','--agent',agent,'--scope','project','--project',project,'--approve-install')
            self.assertNotEqual(b.returncode,0)

    def test_install_refuses_without_approval(self):
        r=self.run_cli('install','--agent','claude','--scope','project','--project',self.project)
        self.assertEqual(r.returncode,2)
        self.assertFalse((self.project/'.claude').exists())

    def test_symlink_not_scanned(self):
        outside=Path(self.temp.name)/'outside.ts'
        outside.write_text('google-analytics.com')
        try:
            (self.project/'link.ts').symlink_to(outside)
        except OSError:
            self.skipTest('Symlinks unsupported')
        self.assertEqual(ulp.scan_project(self.project)['signals_count'],0)


if __name__=='__main__':
    unittest.main()
