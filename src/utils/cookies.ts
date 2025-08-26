export function setCookie(name: string, value: string, days = 180) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
}

export function getCookie(name: string): string | null {
  const target = `${encodeURIComponent(name)}=`;
  const found = document.cookie
    .split(";")
    .map((c) => c.trim())
    .find((c) => c.startsWith(target));
  return found ? decodeURIComponent(found.slice(target.length)) : null;
}
