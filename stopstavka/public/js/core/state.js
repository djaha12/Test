import { useEffect, useState } from '../vendor/preact-htm.js';
import { browserStorage, createStore } from './store.js';
import { toISODate } from '../logic/dates.js';

export const store = createStore({ storage: browserStorage() });

export function useAppState() {
  const [state, setState] = useState(store.get());
  useEffect(() => store.subscribe(setState), []);
  return state;
}

export function todayISO() {
  return toISODate(new Date());
}

export function isPremium(state, now = Date.now()) {
  return Boolean(state.premium?.token && state.premium.exp > now);
}

// Всплывающее сообщение внизу экрана.
let toastHandler = null;
export function onToast(handler) {
  toastHandler = handler;
}
export function showToast(text) {
  toastHandler?.(text);
}

// Маршруты — простые токены после #: #home, #sos, #journal …
export function currentRoute() {
  return globalThis.location.hash.replace(/^#\/?/, '') || '';
}

export function navigate(route) {
  if (currentRoute() !== route) globalThis.location.hash = route;
  else globalThis.scrollTo?.(0, 0);
}

export function useRoute() {
  const [route, setRoute] = useState(currentRoute());
  useEffect(() => {
    const update = () => {
      setRoute(currentRoute());
      globalThis.scrollTo?.(0, 0);
    };
    globalThis.addEventListener('hashchange', update);
    return () => globalThis.removeEventListener('hashchange', update);
  }, []);
  return route;
}
