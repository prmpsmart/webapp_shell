import { Guide } from '../components/Guide'
import configuration from '../../../../docs/CONFIGURATION.md?raw'
import contract from '../../../../docs/CONTRACT.md?raw'
import freezing from '../../../../docs/FREEZING.md?raw'
import nativeFunctions from '../../../../docs/NATIVE_FUNCTIONS.md?raw'
import translating from '../../../../docs/TRANSLATING.md?raw'
import troubleshooting from '../../../../docs/TROUBLESHOOTING.md?raw'

export const ContractGuide = () => <Guide source={contract} />
export const ConfigurationGuide = () => <Guide source={configuration} />
export const NativeFunctionsGuide = () => <Guide source={nativeFunctions} />
export const FreezingGuide = () => <Guide source={freezing} />
export const TranslatingGuide = () => <Guide source={translating} />
export const TroubleshootingGuide = () => <Guide source={troubleshooting} />
