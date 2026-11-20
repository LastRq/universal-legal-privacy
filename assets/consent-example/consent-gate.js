/** NON-PRODUCTION reference. Does not block third-party scripts injected elsewhere. */
export class ConsentGate {
  constructor({key = 'ulp-consent-demo', version = '1', storage = null} = {}) {
    this.key = key;
    this.version = version;
    this.storage = storage ?? (typeof localStorage !== 'undefined' ? localStorage : null);
    this.enabled = new Map();
    this.choices = {analytics: false, marketing: false};
    this.answered = false;
    try {
      const raw = this.storage?.getItem(this.key);
      const saved = raw ? JSON.parse(raw) : null;
      if (saved?.version === this.version &&
          typeof saved.analytics === 'boolean' && typeof saved.marketing === 'boolean') {
        this.choices = {analytics: saved.analytics, marketing: saved.marketing};
        this.answered = true;
      }
    } catch (_) { /* fail closed when storage is disabled or corrupt */ }
  }
  register(category, start, stop = () => {}) {
    if (!['analytics', 'marketing'].includes(category) || typeof start !== 'function' ||
        typeof stop !== 'function') throw new TypeError('Invalid optional capability');
    const item = {start, stop, running:false};
    this.enabled.set(category, [...(this.enabled.get(category) ?? []), item]);
    if (this.answered && this.choices[category]) this._sync();
  }
  _sync() {
    for (const [category, items] of this.enabled) {
      for (const item of items) {
        if (this.answered && this.choices[category] && !item.running) {
          item.start(); item.running = true;
        } else if ((!this.answered || !this.choices[category]) && item.running) {
          item.stop(); item.running = false;
        }
      }
    }
  }
  setChoices(choices) {
    this.choices = {analytics: choices.analytics === true, marketing: choices.marketing === true};
    this.answered = true;
    this._sync();
    try { this.storage?.setItem(this.key, JSON.stringify({version:this.version,...this.choices})); }
    catch (_) { /* ephemeral choice; never misrepresent persistence */ }
  }
  withdraw() { this.setChoices({analytics: false, marketing: false}); }
  snapshot() { return {choices: {...this.choices}, answered: this.answered}; }
}
