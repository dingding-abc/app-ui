export type ColorMode = 'light' | 'dark' | 'light_hc' | 'dark_hc';
export function resolveTokens(document: unknown, themeId: string, mode: ColorMode): Readonly<{
  colors: Readonly<Record<'background' | 'surface' | 'text' | 'secondaryText' | 'action' | 'onAction' | 'actionText' | 'border' | 'dangerText' | 'dangerBackground', string>>;
  cardRadius: number; actionRadius: number; minTargetSize: number; contractVersion: 1;
}>;
