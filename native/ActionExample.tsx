import { useRef, useState } from 'react';
import { ActivityIndicator, Pressable, Text, View } from 'react-native';
import { resolveTokens, type ColorMode } from './resolve-tokens.cjs';
import document from '../design-tokens.json';

// This is a source example. The host supplies safe areas and actual persistence.
export function ActionExample({ themeId = 'A', mode, save }: {
  themeId?: string; mode: ColorMode; save: () => Promise<void>;
}) {
  const tokens = resolveTokens(document, themeId, mode);
  const [pending, setPending] = useState(false);
  const [message, setMessage] = useState('');
  const busy = useRef(false);
  async function submit() {
    if (busy.current) return;
    busy.current = true; setPending(true); setMessage('');
    try { await save(); setMessage('已保存'); }
    catch { setMessage('保存失败，请重试'); }
    finally { busy.current = false; setPending(false); }
  }
  return <View style={{ padding: 16, gap: 12, backgroundColor: tokens.colors.background }}>
    <Text allowFontScaling style={{ color: tokens.colors.text, fontSize: 17 }}>当前内容</Text>
    <Pressable onPress={submit} disabled={pending} accessibilityRole="button"
      accessibilityLabel="保存" accessibilityState={{ disabled: pending, busy: pending }}
      style={{ minHeight: tokens.minTargetSize, minWidth: tokens.minTargetSize,
        paddingVertical: 12, paddingHorizontal: 24, borderRadius: tokens.actionRadius,
        alignItems: 'center', justifyContent: 'center', backgroundColor: tokens.colors.action }}>
      {pending ? <ActivityIndicator color={tokens.colors.onAction} /> :
        <Text allowFontScaling style={{ color: tokens.colors.onAction, fontSize: 17 }}>保存</Text>}
    </Pressable>
    <Text allowFontScaling accessibilityLiveRegion="polite" style={{ color: tokens.colors.text }}>{message}</Text>
  </View>;
}
