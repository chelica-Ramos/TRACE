export default function(component) {
  const {parentElement, data, setStateValue} = component;
  const group = parentElement.querySelector('.trace-language-switch');
  const buttons = [...group.querySelectorAll('button')];
  const storageKey = 'trace.ui.language';
  let selected = data.language;
  // Storage may be disabled; the switch still works for this visit.
  try {
    const saved = localStorage.getItem(storageKey);
    if (saved === 'en' || saved === 'tl') selected = saved;
  } catch (_) {}

  function text(key) {
    const value = data.catalogs[selected][key];
    if (value !== undefined) return value;
    if (data.development) console.warn(`Missing ${selected} translation: ${key}; using English`);
    return data.catalogs.en[key];
  }
  function paint() {
    document.documentElement.lang = selected;
    group.setAttribute('aria-label', text('language_label'));
    buttons.forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.language === selected));
      button.title = text(`language_${button.dataset.language}`);
      button.setAttribute('aria-label', button.title);
    });
  }
  // Localize Streamlit's built-in control tooltips, never table/chart data.
  const nativeKeys = ['native_download', 'native_search', 'native_fullscreen', 'native_close', 'native_clear', 'native_no_rows'];
  function nativeKey(value) {
    return nativeKeys.find(key => value === data.catalogs.en[key] || value === data.catalogs.tl[key]);
  }
  function translateNativeControls() {
    document.querySelectorAll('button[title],button[aria-label],[role="tooltip"],[data-testid="stTooltipContent"]').forEach(element => {
      for (const attribute of ['title', 'aria-label']) {
        const key = nativeKey(element.getAttribute(attribute));
        if (key && element.getAttribute(attribute) !== text(key)) element.setAttribute(attribute, text(key));
      }
      if (element.getAttribute('role') === 'tooltip' || element.dataset.testid === 'stTooltipContent') {
        const key = nativeKey(element.textContent.trim());
        if (key && element.textContent !== text(key)) element.textContent = text(key);
      }
    });
  }
  const observer = new MutationObserver(translateNativeControls);
  observer.observe(document.body, {subtree:true, childList:true, attributes:true, attributeFilter:['title','aria-label']});
  const handlers = buttons.map(button => {
    const handler = () => {
      selected = button.dataset.language;
      try {localStorage.setItem(storageKey, selected);} catch (_) {}
      paint();
      translateNativeControls();
      setStateValue('language', selected);
    };
    button.addEventListener('click', handler);
    return handler;
  });
  paint();
  translateNativeControls();
  if (selected !== data.language) setStateValue('language', selected);
  if (data.development) {
    for (const key of Object.keys(data.catalogs.en)) {
      if (!(key in data.catalogs.tl)) console.warn(`Missing tl translation: ${key}; using English`);
    }
    (data.missing || []).forEach(key => console.warn(`Missing translation: ${key}; using English`));
  }
  return () => {
    observer.disconnect();
    buttons.forEach((button, i) => button.removeEventListener('click', handlers[i]));
  };
}
