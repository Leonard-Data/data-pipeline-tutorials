// Progressive enhancement: the curriculum and examples remain readable without JS.
for (const button of document.querySelectorAll('[data-print]')) {
  button.hidden = false;
  button.addEventListener('click', () => window.print());
}

const contentsOutline = document.querySelector('.contents-outline');
if (contentsOutline) {
  const desktop = window.matchMedia('(min-width: 1200px)');
  const syncOutline = () => { contentsOutline.open = desktop.matches; };
  syncOutline();
  desktop.addEventListener('change', syncOutline);
}

function openTarget(id) {
  const target = document.getElementById(id);
  if (!target) return;
  if (target instanceof HTMLDetailsElement) target.open = true;
  for (let parent = target.parentElement; parent; parent = parent.parentElement) {
    if (parent instanceof HTMLDetailsElement) parent.open = true;
  }
}
openTarget(window.location.hash.slice(1));
window.addEventListener('hashchange', () => openTarget(window.location.hash.slice(1)));
document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href^="#"]');
  if (link) openTarget(link.getAttribute('href').slice(1));
});

for (const pre of document.querySelectorAll('pre:has(code)')) {
  const wrapper = document.createElement('div');
  wrapper.className = 'code-block';
  pre.before(wrapper);
  wrapper.append(pre);
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'copy-code';
  button.textContent = 'Copy code';
  wrapper.append(button);
  button.addEventListener('click', async () => {
    const code = pre.querySelector('code');
    const feedback = document.getElementById('copy-feedback');
    button.disabled = true;
    try {
      if (!navigator.clipboard) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = 'Copied';
      if (feedback) feedback.textContent = 'Code copied to your clipboard.';
    } catch {
      const range = document.createRange();
      range.selectNodeContents(code);
      const selection = window.getSelection();
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = 'Code selected';
      if (feedback) feedback.textContent = 'Clipboard unavailable. Code selected; use your browser’s Copy command.';
    } finally {
      button.disabled = false;
      window.setTimeout(() => { button.textContent = 'Copy code'; }, 2200);
    }
  });
}

const controls = document.getElementById('rerun-controls');
if (controls) {
  controls.hidden = false;
  let batchCopies = 1;
  const feedback = document.getElementById('rerun-feedback');
  function renderBatch() {
    document.getElementById('warehouse-rows').textContent = String(2 * batchCopies);
    document.getElementById('duplicate-keys').textContent = batchCopies > 1 ? '2' : '0';
    // Integer cents keep this synthetic money calculation exact.
    document.getElementById('warehouse-total').textContent = `$${(4500 * batchCopies / 100).toFixed(2)}`;
    feedback.dataset.state = batchCopies > 1 ? 'error' : 'success';
    feedback.textContent = batchCopies > 1
      ? 'Reconciliation failed: the same two business keys were loaded again. The source still totals $45.00.'
      : 'Reconciliation passed: the same two lines still total $45.00. This full-batch replace is idempotent.';
  }
  document.getElementById('run-batch').addEventListener('click', () => {
    const mode = document.querySelector('input[name="write-mode"]:checked').value;
    batchCopies = mode === 'replace' ? 1 : batchCopies + 1;
    renderBatch();
  });
  document.getElementById('reset-batch').addEventListener('click', () => {
    batchCopies = 1;
    document.querySelector('input[name="write-mode"][value="replace"]').checked = true;
    renderBatch();
  });
}

const quiz = document.getElementById('grain-quiz');
if (quiz) {
  quiz.hidden = false;
  quiz.addEventListener('submit', (event) => {
    event.preventDefault();
    const answer = new FormData(quiz).get('grain');
    const feedback = document.getElementById('quiz-feedback');
    feedback.dataset.state = answer === 'line' ? 'success' : 'error';
    feedback.textContent = !answer
      ? 'Choose an answer first. What business event does this model record?'
      : answer === 'line'
        ? 'Correct. One sales order line. Daily totals aggregate facts; product records describe dimensions.'
        : 'Try again. A daily total aggregates many lines, and a product master record describes a dimension. Name the event stored in the fact.';
  });
}

// Native details need opening for consistent printing across browsers.
let printState = [];
window.addEventListener('beforeprint', () => {
  printState = [...document.querySelectorAll('details')].map((details) => [details, details.open]);
  for (const [details] of printState) details.open = true;
});
window.addEventListener('afterprint', () => {
  for (const [details, wasOpen] of printState) details.open = wasOpen;
  printState = [];
});
