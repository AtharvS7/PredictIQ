// Legacy CurrencyToggle — re-exports CurrencySelector for backwards compatibility.
// New code should import CurrencySelector directly.
import CurrencySelector from './CurrencySelector';

export default function CurrencyToggle() {
  return <CurrencySelector compact />;
}
