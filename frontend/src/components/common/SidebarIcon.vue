<template>
  <div class="relative group">
    <div
      :class="[
        'inline-flex items-center justify-center transition-all duration-200',
        size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-6 h-6' : 'w-5 h-5',
        hoverable ? 'hover:scale-110 hover:text-primary-600 cursor-pointer' : '',
        iconClass
      ]"
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
    >
      <component :is="iconComponent" v-if="iconComponent" :class="sizeClass" />
      <component :is="heroIcon" v-else-if="iconName" :class="sizeClass" />
    </div>
    
    <!-- Tooltip -->
    <Transition name="tooltip-fade">
      <div
        v-if="tooltip && showTooltip"
        class="absolute left-full ml-2 top-1/2 -translate-y-1/2 z-50 pointer-events-none"
      >
        <div class="bg-gray-900 dark:bg-gray-800 text-white text-xs py-1.5 px-2.5 rounded-md shadow-lg whitespace-nowrap border border-gray-700">
          {{ tooltip }}
          <div class="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-800"></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as HeroIcons from '@heroicons/vue/24/outline'

const props = defineProps({
  iconName: {
    type: String,
    default: null
  },
  iconComponent: {
    type: [Object, Function],
    default: null
  },
  tooltip: {
    type: String,
    default: null
  },
  size: {
    type: String,
    default: 'md', // 'sm', 'md', 'lg'
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  iconClass: {
    type: String,
    default: 'text-gray-600 dark:text-gray-400'
  }
})

const showTooltip = ref(false)

const sizeClass = computed(() => {
  return props.size === 'sm' ? 'w-4 h-4' : props.size === 'lg' ? 'w-6 h-6' : 'w-5 h-5'
})

// Map icon names to Heroicons v2 components
const iconMap = {
  // Orders & Documents
  'document': HeroIcons.DocumentTextIcon,
  'clipboard': HeroIcons.ClipboardIcon,
  'clipboard-list': HeroIcons.ClipboardDocumentListIcon,
  'clipboard-check': HeroIcons.ClipboardDocumentCheckIcon,
  'credit-card': HeroIcons.CreditCardIcon,
  'check-circle': HeroIcons.CheckCircleIcon,
  'exclamation-triangle': HeroIcons.ExclamationTriangleIcon,
  'clock': HeroIcons.ClockIcon,
  'cog': HeroIcons.Cog6ToothIcon,
  'paper-airplane': HeroIcons.PaperAirplaneIcon,
  'arrow-right': HeroIcons.ArrowRightIcon,
  'arrow-left': HeroIcons.ArrowLeftIcon,
  'search': HeroIcons.MagnifyingGlassIcon,
  
  // Users & People
  'user': HeroIcons.UserIcon,
  'users': HeroIcons.UsersIcon,
  'user-circle': HeroIcons.UserCircleIcon,
  'user-group': HeroIcons.UserGroupIcon,
  'briefcase': HeroIcons.BriefcaseIcon,
  'pencil': HeroIcons.PencilIcon,
  'headphones': HeroIcons.HeadphonesIcon,
  'ticket': HeroIcons.TicketIcon,
  
  // Financial
  'wallet': HeroIcons.WalletIcon,
  'gift': HeroIcons.GiftIcon,
  'star': HeroIcons.StarIcon,
  'dollar-sign': HeroIcons.CurrencyDollarIcon,
  'ban': HeroIcons.NoSymbolIcon,
  
  // Content & Media
  'book': HeroIcons.BookOpenIcon,
  'lightning': HeroIcons.BoltIcon,
  'chart-bar': HeroIcons.ChartBarIcon,
  'trophy': HeroIcons.TrophyIcon,
  'trending-up': HeroIcons.ArrowTrendingUpIcon,
  'trending-down': HeroIcons.ArrowTrendingDownIcon,
  'academic-cap': HeroIcons.AcademicCapIcon,
  
  // Activity & Status
  'calendar': HeroIcons.CalendarIcon,
  'calendar-days': HeroIcons.CalendarDaysIcon,
  'stop': HeroIcons.StopCircleIcon,
  'scale': HeroIcons.ScaleIcon,
  'scroll': HeroIcons.DocumentTextIcon,
  'chat': HeroIcons.ChatBubbleLeftRightIcon,
  'shield': HeroIcons.ShieldCheckIcon,
  'discount': HeroIcons.TagIcon,
  'home': HeroIcons.HomeIcon,
  'plus': HeroIcons.PlusIcon,
  
  // Additional icons
  'folder': HeroIcons.FolderIcon,
  'photograph': HeroIcons.PhotoIcon,
  'collection': HeroIcons.RectangleStackIcon,
  'newspaper': HeroIcons.NewspaperIcon,
  'puzzle': HeroIcons.PuzzlePieceIcon,
  'cube': HeroIcons.CubeIcon,
  'beaker': HeroIcons.BeakerIcon,
  'globe': HeroIcons.GlobeAltIcon,
  'server': HeroIcons.ServerIcon,
  'database': HeroIcons.CircleStackIcon,
  'adjustments': HeroIcons.AdjustmentsHorizontalIcon,
  'bell': HeroIcons.BellIcon,
  'mail': HeroIcons.EnvelopeIcon,
  'inbox': HeroIcons.InboxIcon,
  'tag': HeroIcons.TagIcon,
  'hashtag': HeroIcons.HashtagIcon,
  'link': HeroIcons.LinkIcon,
  'fire': HeroIcons.FireIcon,
  'sparkles': HeroIcons.SparklesIcon,
  'presentation-chart': HeroIcons.PresentationChartLineIcon,
  'calculator': HeroIcons.CalculatorIcon,
  'cash': HeroIcons.BanknotesIcon,
  'receipt-tax': HeroIcons.ReceiptPercentIcon,
  'currency-dollar': HeroIcons.CurrencyDollarIcon,
  'library': HeroIcons.BuildingLibraryIcon,
  'film': HeroIcons.FilmIcon,
  'video-camera': HeroIcons.VideoCameraIcon,
  'microphone': HeroIcons.MicrophoneIcon,
  'speakerphone': HeroIcons.MegaphoneIcon,
  'rss': HeroIcons.RssIcon,
  'megaphone': HeroIcons.MegaphoneIcon,
  'annotation': HeroIcons.ChatBubbleBottomCenterTextIcon,
  'document-text': HeroIcons.DocumentTextIcon,
  'document-duplicate': HeroIcons.DocumentDuplicateIcon,
  'folder-open': HeroIcons.FolderOpenIcon,
  'archive': HeroIcons.ArchiveBoxIcon,
  'cube-transparent': HeroIcons.CubeTransparentIcon,
  'view-grid': HeroIcons.Squares2X2Icon,
  'table': HeroIcons.TableCellsIcon,
  'identification': HeroIcons.IdentificationIcon,
  'badge-check': HeroIcons.CheckBadgeIcon,
  'office-building': HeroIcons.BuildingOfficeIcon,
  'academic-cap-alt': HeroIcons.AcademicCapIcon,
  'light-bulb': HeroIcons.LightBulbIcon,
  'puzzle-piece': HeroIcons.PuzzlePieceIcon,
  'template': HeroIcons.RectangleStackIcon,
  'code': HeroIcons.CodeBracketIcon,
  'terminal': HeroIcons.CommandLineIcon,
  'key': HeroIcons.KeyIcon,
  'lock-closed': HeroIcons.LockClosedIcon,
  'eye': HeroIcons.EyeIcon,
  'eye-off': HeroIcons.EyeSlashIcon,
  'finger-print': HeroIcons.FingerPrintIcon,
  'shield-check': HeroIcons.ShieldCheckIcon,
  'shield-exclamation': HeroIcons.ShieldExclamationIcon,
  'x-circle': HeroIcons.XCircleIcon,
  'check': HeroIcons.CheckIcon,
  'x': HeroIcons.XMarkIcon,
  'plus-circle': HeroIcons.PlusCircleIcon,
  'minus-circle': HeroIcons.MinusCircleIcon,
  'information-circle': HeroIcons.InformationCircleIcon,
  'question-mark-circle': HeroIcons.QuestionMarkCircleIcon,
  'exclamation-circle': HeroIcons.ExclamationCircleIcon,
  'clock-fast': HeroIcons.BoltIcon,
  'pause': HeroIcons.PauseCircleIcon,
  'play': HeroIcons.PlayCircleIcon,
  'refresh': HeroIcons.ArrowPathIcon,
  'arrow-up': HeroIcons.ArrowUpIcon,
  'arrow-down': HeroIcons.ArrowDownIcon,
  'arrow-up-right': HeroIcons.ArrowUpRightIcon,
  'arrow-down-right': HeroIcons.ArrowDownRightIcon,
  'arrow-down-left': HeroIcons.ArrowDownLeftIcon,
  'arrow-up-left': HeroIcons.ArrowUpLeftIcon,
  'chevron-up': HeroIcons.ChevronUpIcon,
  'chevron-down': HeroIcons.ChevronDownIcon,
  'chevron-left': HeroIcons.ChevronLeftIcon,
  'chevron-right': HeroIcons.ChevronRightIcon,
  'dots-vertical': HeroIcons.EllipsisVerticalIcon,
  'dots-horizontal': HeroIcons.EllipsisHorizontalIcon,
  'menu': HeroIcons.Bars3Icon,
  'menu-alt-1': HeroIcons.Bars3BottomLeftIcon,
  'menu-alt-2': HeroIcons.Bars3BottomRightIcon,
  'menu-alt-3': HeroIcons.Bars3Icon,
  'menu-alt-4': HeroIcons.Bars3Icon,
  'filter': HeroIcons.FunnelIcon,
  'sort-ascending': HeroIcons.ArrowUpIcon,
  'sort-descending': HeroIcons.ArrowDownIcon,
  'switch-vertical': HeroIcons.ArrowsUpDownIcon,
  'switch-horizontal': HeroIcons.ArrowsRightLeftIcon,
  'view-list': HeroIcons.ListBulletIcon,
  'view-grid-add': HeroIcons.SquaresPlusIcon,
  'dots-circle-horizontal': HeroIcons.EllipsisHorizontalCircleIcon,
  'dots-circle': HeroIcons.EllipsisHorizontalCircleIcon,
  'dots': HeroIcons.EllipsisHorizontalIcon,
  'dots-grid': HeroIcons.Squares2X2Icon,
  'dots-square': HeroIcons.Squares2X2Icon,
  'dots-hexagon': HeroIcons.HexagonIcon,
  'dots-diamond': HeroIcons.SparklesIcon,
  'dots-ellipsis': HeroIcons.EllipsisHorizontalCircleIcon,
}

const heroIcon = computed(() => {
  if (!props.iconName) return null
  const icon = iconMap[props.iconName]
  return icon || HeroIcons.QuestionMarkCircleIcon // Fallback icon
})
</script>

<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-4px);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateX(0);
}
</style>
