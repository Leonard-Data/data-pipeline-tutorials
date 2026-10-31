// Reusable lesson practice; no network requests or stored learning claims.
for (const form of document.querySelectorAll('form[data-quiz]')) {
  const controls = form.querySelector('[data-quiz-controls]');
  const feedback = form.querySelector('[data-quiz-feedback]');
  controls.hidden = false;
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const selected = form.querySelector('input[type="radio"]:checked');
    if (!selected) {
      feedback.dataset.state = 'error';
      feedback.textContent = 'Choose an answer first, then explain your reasoning.';
      return;
    }
    const correct = selected.value === form.dataset.correct;
    feedback.dataset.state = correct ? 'success' : 'error';
    feedback.textContent = `${correct ? 'Correct.' : 'Try again.'} ${selected.dataset.feedback}`;
  });
  form.addEventListener('change', () => {
    delete feedback.dataset.state;
    feedback.textContent = 'Answer changed. Check this choice when you are ready.';
  });
}

for (const lab of document.querySelectorAll('[data-delivery-lab]')) {
  let received = 0;
  let batchSeen = 0;
  const feedback = lab.querySelector('[data-delivery-feedback]');
  lab.querySelector('[data-delivery-controls]').hidden = false;
  function render() {
    lab.querySelector('[data-source-count]').textContent = String(received);
    lab.querySelector('[data-stream-count]').textContent = String(received);
    lab.querySelector('[data-batch-count]').textContent = String(batchSeen);
  }
  lab.querySelector('[data-receive]').addEventListener('click', () => {
    received += 1;
    render();
    feedback.textContent = `Order ${received} arrived. The event consumer has seen it; the batch is behind by ${received - batchSeen}.`;
  });
  lab.querySelector('[data-run-batch]').addEventListener('click', () => {
    batchSeen = received;
    render();
    feedback.textContent = `Scheduled batch finished. Both consumers have now seen ${received} orders. New arrivals will wait for the next batch.`;
  });
  lab.querySelector('[data-reset-delivery]').addEventListener('click', () => {
    received = 0;
    batchSeen = 0;
    render();
    feedback.textContent = 'Arrivals reset. Predict the result before receiving the next order.';
  });
}
