// Copy pip install command
const copyBtn = document.getElementById('copy-pip-btn');
const copyText = document.getElementById('copy-pip-text');
const pipCmd = document.getElementById('pip-cmd');

if (copyBtn && copyText && pipCmd) {
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(pipCmd.textContent.trim());
      copyText.textContent = 'Copied!';
      setTimeout(() => {
        copyText.textContent = 'Copy';
      }, 1800);
    } catch {
      copyText.textContent = 'pip install afrogeo';
    }
  });
}

// Usage Tabs
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    const target = btn.getAttribute('data-tab');
    tabButtons.forEach((b) => b.classList.remove('active'));
    tabPanels.forEach((p) => p.classList.remove('active'));

    btn.classList.add('active');
    const panel = document.getElementById(`tab-${target}`);
    if (panel) panel.classList.add('active');
  });
});

// Interactive Playground Presets
const presets = {
  valid_full: {
    valid: true,
    input: `{
  "country": "Nigeria",
  "state": "Lagos",
  "lga": "Agege",
  "city": "Agege"
}`,
    output: `<AfrogeoResult valid=True country='NG' state='Lagos'>

result.normalized = {
  "country_code": "NG",
  "country": "Nigeria",
  "country_name": "Nigeria",
  "levels": { "level_1": "State", "level_2": "LGA" },
  "level_1_label": "State",
  "level_2_label": "LGA",
  "state_code": "LA",
  "state": "Lagos",
  "capital": "Ikeja",
  "lga": "Agege",
  "city": "Agege",
  "division_1_code": "LA",
  "division_1_name": "Lagos",
  "division_2_name": "Agege",
  "settlement": "Agege",
  "settlements": ["Agege", "Oko-Oba", "Dopemu", ...]
}`,
  },
  valid_codes: {
    valid: true,
    input: `{
  "country": "ng",
  "state": "ed",
  "lga": "oredo"
}`,
    output: `<AfrogeoResult valid=True country='NG' state='Edo'>

result.normalized = {
  "country_code": "NG",
  "country": "Nigeria",
  "state_code": "ED",
  "state": "Edo",
  "capital": "Benin City",
  "lga": "Oredo",
  "city": null,
  "division_1_code": "ED",
  "division_1_name": "Edo",
  "division_2_name": "Oredo",
  "settlement": null
}`,
  },
  invalid_lga: {
    valid: false,
    input: `{
  "country": "Nigeria",
  "state": "Lagos",
  "lga": "NonExistentLGA"
}`,
    output: `<AfrogeoResult valid=False errors=['Invalid LGA for selected state']>

result.valid      # False
result.errors     # ["Invalid LGA for selected state"]
result.normalized # {}`,
  },
  invalid_settlement: {
    valid: false,
    input: `{
  "country": "NG",
  "state": "LA",
  "lga": "Agege",
  "city": "UnknownTown"
}`,
    output: `<AfrogeoResult valid=False errors=['Settlement does not match LGA']>

result.valid      # False
result.errors     # ["Settlement does not match LGA"]
result.normalized # {}`,
  },
};

const inputEl = document.getElementById('playground-input');
const outputEl = document.getElementById('playground-output');
const statusEl = document.getElementById('playground-status');
const presetButtons = document.querySelectorAll('.preset-btn');

function renderPreset(key) {
  const item = presets[key];
  if (!item || !inputEl || !outputEl || !statusEl) return;

  inputEl.textContent = item.input;
  outputEl.textContent = item.output;
  if (item.valid) {
    statusEl.textContent = 'result.valid = True';
    statusEl.className = 'status-pill valid';
  } else {
    statusEl.textContent = 'result.valid = False';
    statusEl.className = 'status-pill invalid';
  }
}

presetButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    presetButtons.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    renderPreset(btn.getAttribute('data-preset'));
  });
});

renderPreset('valid_full');

