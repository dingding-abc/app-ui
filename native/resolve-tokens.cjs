'use strict';

// Contract 1 maps semantic roles only; system fonts, safe areas and behavior
// remain the consuming application's responsibility.
const modes = new Set(['light', 'dark', 'light_hc', 'dark_hc']);
const roles = {
  background: 'bg', surface: 'surface', text: 'ink', secondaryText: 'sub',
  action: 'accent', onAction: 'on_accent', actionText: 'accent_text',
  border: 'control_border', dangerText: 'danger_text', dangerBackground: 'danger_soft',
};
function resolveTokens(document, themeId, mode) {
  if (document?.native_contract_version !== 1 || document.version !== '5.1') {
    throw new Error('Unsupported native token contract; regenerate or migrate explicitly');
  }
  if (!modes.has(mode)) throw new Error('Unknown color mode');
  if (!Object.hasOwn(document.themes ?? {}, themeId)) throw new Error('Unknown theme');
  const palette = document.themes[themeId][mode];
  if (!palette) throw new Error('Missing requested color mode');
  const colors = Object.fromEntries(Object.entries(roles).map(([role, key]) => {
    const value = palette[key];
    if (typeof value !== 'string' || !/^#[0-9a-f]{6}$/i.test(value)) throw new Error(`Invalid color ${key}`);
    return [role, value];
  }));
  // Geometry is mode-independent in 5.1 and stored on the light palette.
  const cardRadius = /^([0-9]+(?:\.[0-9]+)?)px$/.exec(document.themes[themeId].light?.r_card);
  // CSS percentage radii are intentionally not converted to RN dimensions.
  if (!cardRadius || !Number.isFinite(Number(cardRadius[1]))) throw new Error('Invalid card radius');
  return Object.freeze({ colors: Object.freeze(colors), cardRadius: Number(cardRadius[1]),
    actionRadius: 999, minTargetSize: 44, contractVersion: 1 });
}
module.exports = { resolveTokens };
