const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('#site-nav');

navToggle?.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', String(open));
});

nav?.addEventListener('click', (event) => {
  if (event.target.matches('a')) {
    nav.classList.remove('open');
    navToggle?.setAttribute('aria-expanded', 'false');
  }
});

document.querySelector('[data-copy]')?.addEventListener('click', async (event) => {
  const button = event.currentTarget;
  const code = document.querySelector('.terminal code')?.textContent ?? '';
  try {
    await navigator.clipboard.writeText(code);
    button.textContent = 'Copied';
    setTimeout(() => { button.textContent = 'Copy'; }, 1600);
  } catch {
    button.textContent = 'Select text';
  }
});

const workflow = document.querySelector('[data-workflow]');
const precisionSelect = document.querySelector('#demo-precision');
const runButton = document.querySelector('[data-demo-run]');
const progress = workflow?.querySelector('.demo-progress');
const progressBar = progress?.querySelector('span');
const workflowSteps = [...(workflow?.querySelectorAll('[data-step]') ?? [])];
const statusText = document.querySelector('#demo-status');

const formats = {
  fp32: { label: 'FP32', detail: '32-bit floating-point baseline', bits: 32, reduction: 'reference storage' },
  bf16: { label: 'BF16', detail: '16-bit reduced-precision float', bits: 16, reduction: '2× below FP32' },
  int8: { label: 'INT8', detail: 'symmetric integer', bits: 8, reduction: '4× below FP32' },
  fxp8: { label: 'FXP8 Q3.4', detail: 'fixed-point arithmetic', bits: 8, reduction: '4× below FP32' },
  p82: { label: 'Posit(8,2)', detail: '8-bit posit codebook', bits: 8, reduction: '4× below FP32' },
  p41: { label: 'Posit(4,1)', detail: '4-bit posit codebook', bits: 4, reduction: '8× below FP32' },
  e2m1: { label: 'HFP4 E2M1', detail: '4-bit minifloat', bits: 4, reduction: '8× below FP32' },
  e3m0: { label: 'HFP4 E3M0', detail: '4-bit minifloat', bits: 4, reduction: '8× below FP32' }
};

const workflowMessages = [
  'Reading a 0.8 s mono acoustic segment',
  'Normalizing the waveform and extracting features',
  'Executing the source-aligned 1D-F-CNN',
  'Mapping operands to the selected numeric format',
  'Executing shared-MAC and SRAM-timed RTL models',
  'Producing the binary UAV / non-UAV decision'
];

function updateFormat() {
  const format = formats[precisionSelect?.value] ?? formats.int8;
  document.querySelector('#precision-mark').textContent = format.label;
  document.querySelector('#precision-detail').textContent = `${format.bits}-bit operands`;
  document.querySelector('#readout-format').textContent = `${format.label} · ${format.detail}`;
  document.querySelector('#readout-storage').textContent = `${format.bits} bits · ${format.reduction}`;
  if (!runButton?.disabled) statusText.textContent = `Ready · ${format.label} selected`;
}

precisionSelect?.addEventListener('change', updateFormat);

runButton?.addEventListener('click', async () => {
  runButton.disabled = true;
  precisionSelect.disabled = true;
  workflowSteps.forEach(step => step.classList.remove('active', 'complete'));
  progressBar.style.width = '0%';
  progress.setAttribute('aria-valuenow', '0');
  const delay = matchMedia('(prefers-reduced-motion: reduce)').matches ? 180 : 780;

  for (let index = 0; index < workflowSteps.length; index += 1) {
    workflowSteps.forEach((step, stepIndex) => {
      step.classList.toggle('active', stepIndex === index);
      step.classList.toggle('complete', stepIndex < index);
    });
    const value = Math.round(((index + 1) / workflowSteps.length) * 100);
    progressBar.style.width = `${value}%`;
    progress.setAttribute('aria-valuenow', String(value));
    statusText.textContent = workflowMessages[index];
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  workflowSteps.forEach(step => { step.classList.remove('active'); step.classList.add('complete'); });
  statusText.textContent = 'Walkthrough complete · illustrative execution only';
  runButton.textContent = 'Run again';
  runButton.disabled = false;
  precisionSelect.disabled = false;
});

updateFormat();

const deploymentPanel = document.querySelector('[data-deployment]');
const deploymentButtons = [...document.querySelectorAll('[data-deployment-view]')];
const deploymentTitle = document.querySelector('#deployment-title');
const deploymentDetail = document.querySelector('#deployment-detail');

const deploymentViews = {
  all: {
    title: 'End-to-end validation concept',
    detail: 'ASIC carrier integration → FPGA prototype validation → acoustic sensing, classification, and tracking.'
  },
  asic: {
    title: 'Proposed ASIC carrier',
    detail: 'Target integration of the low-precision accelerator with memory, power delivery, and sensor interfaces on a compact PCB.'
  },
  fpga: {
    title: 'VC707 FPGA validation',
    detail: 'Virtex-7 VC707 prototyping of the accelerator data path and interfaces before committing the architecture to silicon.'
  },
  field: {
    title: 'Acoustic field-evaluation concept',
    detail: 'A ground acoustic array captures the UAV signature; the accelerator classifies the event and supplies detections to the tracking layer.'
  }
};

deploymentButtons.forEach(button => {
  button.addEventListener('click', () => {
    const view = button.dataset.deploymentView;
    const content = deploymentViews[view] ?? deploymentViews.all;
    deploymentPanel.dataset.focus = view;
    deploymentButtons.forEach(item => {
      const selected = item === button;
      item.classList.toggle('active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    deploymentTitle.textContent = content.title;
    deploymentDetail.textContent = content.detail;
  });
});
