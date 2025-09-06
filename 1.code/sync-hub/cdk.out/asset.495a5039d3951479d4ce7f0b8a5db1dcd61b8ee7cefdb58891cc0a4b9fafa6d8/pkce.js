// RFC 7636 PKCE helpers
async function sha256(buffer) {
  const enc = new TextEncoder();
  const data = enc.encode(buffer);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return new Uint8Array(hash);
}

function base64url(bytes) {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function randString(len=64) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  let out = "";
  const arr = new Uint32Array(len);
  crypto.getRandomValues(arr);
  for (let i=0;i<len;i++) out += chars[arr[i] % chars.length];
  return out;
}

async function makePkce() {
  const code_verifier = randString(64);
  const hash = await sha256(code_verifier);
  const code_challenge = base64url(hash);
  return { code_verifier, code_challenge, method: "S256" };
}

window.PKCE = { makePkce };
