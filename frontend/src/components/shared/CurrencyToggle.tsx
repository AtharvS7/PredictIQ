// Compatibility re-export of CurrencySelector for components.
// Standard code imports CurrencySelector directly.
import CurrencySelector from './CurrencySelector';

export default function CurrencyToggle() {
  return <CurrencySelector compact />;
}
