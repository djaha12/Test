// Шаги защиты. platform: 'all' | 'android' | 'ios'; countries — где шаг применим.
export const STEPS = [
  { id: 'apps', platform: 'all', countries: ['kg', 'kz'] },
  { id: 'dns', platform: 'all', countries: ['kg', 'kz'], showDomains: true },
  { id: 'ios', platform: 'ios', countries: ['kg', 'kz'], showDomains: true },
  { id: 'play', platform: 'android', countries: ['kg', 'kz'] },
  { id: 'cards', platform: 'all', countries: ['kg', 'kz'] },
  { id: 'channels', platform: 'all', countries: ['kg', 'kz'] },
  { id: 'selfban', platform: 'all', countries: ['kz'] },
  { id: 'tell', platform: 'all', countries: ['kg', 'kz'] },
];

export function stepsFor(country) {
  return STEPS.filter((s) => s.countries.includes(country || 'kg'));
}

// Примерный список адресов букмекеров и онлайн-казино. Адреса часто меняются —
// основная защита — фильтр по категории Gambling. Список стоит обновлять раз в месяц.
export const DOMAINS = [
  '1xbet.com', '1xbet.kz', 'melbet.com', 'mostbet.com', '1win.com', '1win.pro',
  'pin-up.casino', 'olimpbet.kz', 'fonbet.kz', 'fonbet.ru', 'tennisi.kz', 'parimatch.kz',
  'betboom.ru', 'leon.ru', 'winline.ru', 'marathonbet.com', 'vavada.com', 'pokerdom.com', 'joycasino.com',
];
