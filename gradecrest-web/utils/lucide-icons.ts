import { defineComponent, h } from 'vue'

type IconNode = [string, Record<string, string | number>]

const createIcon = (name: string, nodes: IconNode[]) =>
  defineComponent({
    name,
    inheritAttrs: false,
    props: {
      size: { type: [Number, String], default: 24 },
      color: { type: String, default: 'currentColor' },
      strokeWidth: { type: [Number, String], default: 2 },
    },
    setup(props, { attrs }) {
      return () =>
        h(
          'svg',
          {
            xmlns: 'http://www.w3.org/2000/svg',
            width: props.size,
            height: props.size,
            viewBox: '0 0 24 24',
            fill: 'none',
            stroke: props.color,
            'stroke-width': props.strokeWidth,
            'stroke-linecap': 'round',
            'stroke-linejoin': 'round',
            ...attrs,
          },
          nodes.map(([tag, nodeAttrs]) => h(tag, nodeAttrs)),
        )
    },
  })

export const ArrowLeft = createIcon('ArrowLeft', [
  ['path', { d: 'm12 19-7-7 7-7' }],
  ['path', { d: 'M19 12H5' }],
])

export const ArrowRight = createIcon('ArrowRight', [
  ['path', { d: 'M5 12h14' }],
  ['path', { d: 'm12 5 7 7-7 7' }],
])

export const Calendar = createIcon('Calendar', [
  ['path', { d: 'M8 2v4' }],
  ['path', { d: 'M16 2v4' }],
  ['rect', { x: 3, y: 4, width: 18, height: 18, rx: 2 }],
  ['path', { d: 'M3 10h18' }],
])

export const CheckCircle2 = createIcon('CheckCircle2', [
  ['circle', { cx: 12, cy: 12, r: 10 }],
  ['path', { d: 'm9 12 2 2 4-4' }],
])

export const Check = createIcon('Check', [
  ['path', { d: 'M20 6 9 17l-5-5' }],
])

export const Clock = createIcon('Clock', [
  ['circle', { cx: 12, cy: 12, r: 10 }],
  ['path', { d: 'M12 6v6l4 2' }],
])

export const DollarSign = createIcon('DollarSign', [
  ['path', { d: 'M12 2v20' }],
  ['path', { d: 'M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6' }],
])

export const HelpCircle = createIcon('HelpCircle', [
  ['circle', { cx: 12, cy: 12, r: 10 }],
  ['path', { d: 'M9.1 9a3 3 0 1 1 5.8 1c-.5.9-1.4 1.3-2.1 1.9-.6.5-.8.9-.8 2.1' }],
  ['path', { d: 'M12 17h.01' }],
])

export const Home = createIcon('Home', [
  ['path', { d: 'm3 10 9-7 9 7' }],
  ['path', { d: 'M5 10v10h14V10' }],
  ['path', { d: 'M9 20v-6h6v6' }],
])

export const Lock = createIcon('Lock', [
  ['rect', { x: 3, y: 11, width: 18, height: 11, rx: 2, ry: 2 }],
  ['path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' }],
])

export const Mail = createIcon('Mail', [
  ['rect', { x: 2, y: 4, width: 20, height: 16, rx: 2 }],
  ['path', { d: 'm22 7-8.97 5.7a2 2 0 0 1-2.06 0L2 7' }],
])

export const Menu = createIcon('Menu', [
  ['path', { d: 'M4 12h16' }],
  ['path', { d: 'M4 6h16' }],
  ['path', { d: 'M4 18h16' }],
])

export const MessageSquare = createIcon('MessageSquare', [
  ['path', { d: 'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z' }],
])

export const Minus = createIcon('Minus', [
  ['path', { d: 'M5 12h14' }],
])

export const Plus = createIcon('Plus', [
  ['path', { d: 'M5 12h14' }],
  ['path', { d: 'M12 5v14' }],
])

export const Printer = createIcon('Printer', [
  ['path', { d: 'M6 9V2h12v7' }],
  ['path', { d: 'M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2' }],
  ['path', { d: 'M6 14h12v8H6z' }],
])

export const RefreshCw = createIcon('RefreshCw', [
  ['path', { d: 'M3 12a9 9 0 0 1 15.3-6.4L21 8' }],
  ['path', { d: 'M21 3v5h-5' }],
  ['path', { d: 'M21 12a9 9 0 0 1-15.3 6.4L3 16' }],
  ['path', { d: 'M3 21v-5h5' }],
])

export const Search = createIcon('Search', [
  ['circle', { cx: 11, cy: 11, r: 8 }],
  ['path', { d: 'm21 21-4.3-4.3' }],
])

export const Shield = createIcon('Shield', [
  ['path', { d: 'M20 13c0 5-3.5 7.5-7.3 8.8a2 2 0 0 1-1.4 0C7.5 20.5 4 18 4 13V6a2 2 0 0 1 1.1-1.8l6-2.7a2 2 0 0 1 1.8 0l6 2.7A2 2 0 0 1 20 6z' }],
])

export const Star = createIcon('Star', [
  ['path', { d: 'm12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8-6.2-3.3L5.8 21 7 14.2 2 9.3l6.9-1z' }],
])

export const Tag = createIcon('Tag', [
  ['path', { d: 'M20.6 13.1 13 20.7a2 2 0 0 1-2.8 0L3 13.4V3h10.4l7.2 7.2a2 2 0 0 1 0 2.9z' }],
  ['path', { d: 'M7.5 7.5h.01' }],
])

export const X = createIcon('X', [
  ['path', { d: 'M18 6 6 18' }],
  ['path', { d: 'm6 6 12 12' }],
])

export const BadgeCheck = createIcon('BadgeCheck', [
  ['path', { d: 'M3.9 8.7a2 2 0 0 1 .8-2.2l1.8-1a2 2 0 0 0 1-1.8V3a2 2 0 0 1 2-2h5a2 2 0 0 1 2 2v.7a2 2 0 0 0 1 1.8l1.8 1a2 2 0 0 1 .8 2.2l-.7 2a2 2 0 0 0 0 1.3l.7 2a2 2 0 0 1-.8 2.2l-1.8 1a2 2 0 0 0-1 1.8v.7a2 2 0 0 1-2 2h-5a2 2 0 0 1-2-2V19a2 2 0 0 0-1-1.8l-1.8-1a2 2 0 0 1-.8-2.2l.7-2a2 2 0 0 0 0-1.3z' }],
  ['path', { d: 'm9 12 2 2 4-4' }],
])

export const Banknote = createIcon('Banknote', [
  ['rect', { x: 2, y: 6, width: 20, height: 12, rx: 2 }],
  ['circle', { cx: 12, cy: 12, r: 2 }],
  ['path', { d: 'M6 12h.01M18 12h.01' }],
])

export const BookOpen = createIcon('BookOpen', [
  ['path', { d: 'M12 7v14' }],
  ['path', { d: 'M3 18a2 2 0 0 1 2-2h7V5H5a2 2 0 0 0-2 2z' }],
  ['path', { d: 'M21 18a2 2 0 0 0-2-2h-7V5h7a2 2 0 0 1 2 2z' }],
])

export const Bot = createIcon('Bot', [
  ['path', { d: 'M12 8V4H8' }],
  ['rect', { x: 4, y: 8, width: 16, height: 12, rx: 2 }],
  ['path', { d: 'M2 14h2M20 14h2M9 13v2M15 13v2' }],
])

export const Briefcase = createIcon('Briefcase', [
  ['path', { d: 'M10 6V5a2 2 0 0 1 2-2h0a2 2 0 0 1 2 2v1' }],
  ['rect', { x: 3, y: 6, width: 18, height: 14, rx: 2 }],
  ['path', { d: 'M3 12h18' }],
])

export const ChevronDown = createIcon('ChevronDown', [
  ['path', { d: 'm6 9 6 6 6-6' }],
])

export const FileText = createIcon('FileText', [
  ['path', { d: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z' }],
  ['path', { d: 'M14 2v6h6' }],
  ['path', { d: 'M16 13H8M16 17H8M10 9H8' }],
])

export const GraduationCap = createIcon('GraduationCap', [
  ['path', { d: 'M22 10 12 5 2 10l10 5z' }],
  ['path', { d: 'M6 12v5c3 2 9 2 12 0v-5' }],
])

export const Trophy = createIcon('Trophy', [
  ['path', { d: 'M8 21h8' }],
  ['path', { d: 'M12 17v4' }],
  ['path', { d: 'M7 4h10v6a5 5 0 0 1-10 0z' }],
  ['path', { d: 'M5 9H4a2 2 0 0 1 0-4h3M19 9h1a2 2 0 0 0 0-4h-3' }],
])

export const Upload = createIcon('Upload', [
  ['path', { d: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4' }],
  ['path', { d: 'm17 8-5-5-5 5' }],
  ['path', { d: 'M12 3v12' }],
])

export const Users = createIcon('Users', [
  ['path', { d: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2' }],
  ['circle', { cx: 9, cy: 7, r: 4 }],
  ['path', { d: 'M22 21v-2a4 4 0 0 0-3-3.9' }],
  ['path', { d: 'M16 3.1a4 4 0 0 1 0 7.8' }],
])

export const Zap = createIcon('Zap', [
  ['path', { d: 'M13 2 3 14h9l-1 8 10-12h-9z' }],
])
