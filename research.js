const stages = {
  capture: { visual: 'capture', kicker: 'STAGE 01 · SENSOR INPUT', title: 'Capture a compact camera frame', text: 'The Raspberry Pi camera supplies a 160 × 120 colour image. The small frame limits processing cost and defines the coordinate system used by every later calculation.', config: '160 × 120 pixels · 20 Hz', limit: 'A frame is a sensor observation, not an independent measurement of physical lateral position.', link: './index.html#methods' },
  roi: { visual: 'roi', kicker: 'STAGE 02 · ROAD REGION', title: 'Restrict processing to the track', text: 'The detector begins at 55% of image height. Focusing on the lower road region reduces irrelevant image content and keeps the tested geometry tied to the near track.', config: 'ROI starts at relative height 0.55', limit: 'Changing camera pitch or mounting height changes which physical area the same pixel row represents.', link: './index.html#methods' },
  segment: { visual: 'segment', kicker: 'STAGE 03 · COLOUR EVIDENCE', title: 'Separate white and yellow markings', text: 'HSV thresholds form two binary masks. A 1 × 3 opening protects thin white markings; the yellow mask uses 3 × 3 opening and closing to suppress isolated noise and fill small gaps.', config: 'White HSV [0,0,145]–[179,80,255] · Yellow [15,60,80]–[40,255,255]', limit: 'Fixed colour thresholds remain dependent on illumination, exposure, reflections and the physical marking material.', link: 'https://docs.opencv.org/4.x/d7/da8/tutorial_table_of_content_imgproc.html' },
  pair: { visual: 'pair', kicker: 'STAGE 04 · GEOMETRIC EVIDENCE', title: 'Accept a plausible boundary pair', text: 'Candidate white and yellow positions are checked across image heights. Width, continuity and dark-road evidence help reject combinations that do not resemble the marked lane.', config: 'Selected rows form centre samples; limited interpolation is allowed', limit: 'Output availability measures whether the rules produced a target. It is not recognition accuracy without independent ground truth.', link: './reader.html?file=reports%2FOpenCV%E9%98%B6%E6%AE%B5%E6%80%BB%E7%BB%93_2026-09-07%E8%87%B309-08.md' },
  target: { visual: 'target', kicker: 'STAGE 05 · IMAGE-SPACE TARGETS', title: 'Estimate near and far lane centres', text: 'The midpoint between accepted boundaries supplies a centre position. A near target represents current displacement; a far target adds information about the visible road direction.', config: 'Near r = 0.65 (y = 78) · far r = 0.55 or 0.60', limit: 'The targets are pixel coordinates. They are not calibrated lateral distance or heading angle.', link: './index.html#methods' },
  steer: { visual: 'steer', kicker: 'STAGE 06 · PREVIEW CONTROL', title: 'Convert image error into steering', text: 'Normalised near error and the difference between far and near errors form a preview term. The result is clipped, scaled and mapped to the archived servo request range.', config: 'Centre 365 · limits 290–440 · preview weight 1.5', limit: 'PWM values depend on servo orientation and calibration. They cannot be transferred safely to different hardware unchanged.', link: './index.html#methods' },
  gate: { visual: 'gate', kicker: 'STAGE 07 · MOTION GATE', title: 'Permit motion only after fresh evidence', text: 'Forward request 400 is allowed after five consecutive usable, fresh frames. Lane loss or freshness failure latches stop request 370; a watchdog and duration limit bound the run.', config: '5 ready frames · 0.2 s freshness · 0.25 s watchdog · 16 s limit', limit: 'Software requests cannot guarantee actuator response after a hardware or I²C failure; direct supervision remains necessary.', link: './deployment.html#controller' }
};

const buttons = [...document.querySelectorAll('.pipeline-step')];
const fields = {
  visual: document.querySelector('#stage-visual'), kicker: document.querySelector('#stage-kicker'), title: document.querySelector('#stage-title'),
  text: document.querySelector('#stage-text'), config: document.querySelector('#stage-config'), limit: document.querySelector('#stage-limit'), link: document.querySelector('#stage-link')
};
buttons.forEach(button => button.addEventListener('click', () => {
  const stage = stages[button.dataset.stage];
  buttons.forEach(item => { item.classList.toggle('active', item === button); item.setAttribute('aria-selected', item === button ? 'true' : 'false'); });
  fields.visual.dataset.visual = stage.visual; fields.kicker.textContent = stage.kicker; fields.title.textContent = stage.title; fields.text.textContent = stage.text;
  fields.config.textContent = stage.config; fields.limit.textContent = stage.limit; fields.link.href = stage.link;
}));

const glossaryInput = document.querySelector('#glossary-input');
const glossaryItems = [...document.querySelectorAll('#glossary-grid article')];
const glossaryEmpty = document.querySelector('#glossary-empty');
glossaryInput?.addEventListener('input', () => {
  const query = glossaryInput.value.trim().toLowerCase(); let count = 0;
  glossaryItems.forEach(item => { const show = !query || `${item.dataset.term} ${item.textContent}`.toLowerCase().includes(query); item.hidden = !show; if (show) count += 1; });
  glossaryEmpty.hidden = count > 0;
});
