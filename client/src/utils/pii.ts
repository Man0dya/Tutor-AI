// Lightweight PII detector for client-side warnings only (non-blocking)
// Keep patterns conservative to avoid noisy false positives

const EMAIL = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/;
const PHONE = /\b(?:\+?\d{1,3}[-.\s]?)?(?:\(\d{2,4}\)[-.\s]?|\d{2,4}[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b/;
const SSN = /\b\d{3}-\d{2}-\d{4}\b/;
const IBAN = /\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b/;

function luhnCheck(number: string): boolean {
  const digits = (number.match(/\d/g) || []).map((d) => parseInt(d, 10));
  if (digits.length < 13 || digits.length > 19) return false;
  let checksum = 0;
  const parity = (digits.length - 2) % 2;
  for (let i = 0; i < digits.length - 1; i++) {
    let d = digits[i];
    if (i % 2 === parity) {
      d *= 2;
      if (d > 9) d -= 9;
    }
    checksum += d;
  }
  return (checksum + digits[digits.length - 1]) % 10 === 0;
}

export function detectPII(text?: string): string[] {
  if (!text) return [];
  const issues: string[] = [];
  if (EMAIL.test(text)) issues.push('email');
  if (PHONE.test(text)) issues.push('phone');
  if (SSN.test(text)) issues.push('ssn');
  if (IBAN.test(text)) issues.push('iban');
  // Potential credit card sequences
  const ccMatches = text.match(/\b(?:\d[ -]?){13,19}\b/g) || [];
  if (ccMatches.some((m) => luhnCheck(m))) issues.push('credit card');
  return Array.from(new Set(issues));
}

export function hasPII(text?: string): boolean {
  return detectPII(text).length > 0;
}
