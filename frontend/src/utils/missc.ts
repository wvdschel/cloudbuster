export function readNumber(r) { if ("" === r || "number" != typeof r && "string" != typeof r) return null; var t = Number(r); return Number.isNaN(t) ? null : t }

export function isEmpty(x: any) {
  return (
    x === null ||
    x === undefined ||
    x === '' ||
    (typeof x == 'string' && x?.trim() === '')
  )
}

export function isEmptyObject(obj) {
  return Object.keys(obj).length === 0 && obj.constructor === Object
}


function isValidLink(value:string) {
  try {
    new URL(value);
    return true;
  } catch (error) {
    return false;
  }
}
export function isUrl(value:any) {
  return (
    typeof value === 'string' &&
    (value.startsWith('http://') || value.startsWith('https://')) && isValidLink(value)
  )
}