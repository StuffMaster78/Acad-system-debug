# Discounts App

A robust Django app for managing, validating, stacking, and applying discount codes to orders.  
Supports advanced business rules, stacking logic, usage tracking, suggestions, and more.

---

## Features

- **Discount Code Validation:**  
  Ensures codes are valid, active, within usage limits, and formatted correctly.
- **Advanced Stacking:**  
  Supports stacking flags, stacking groups, stacking priority, and explicit stacking rules.
- **Tiered Discounts:**  
  Apply different discount rates based on order value tiers.
- **Usage Tracking:**  
  Tracks per-user and global usage, prevents overuse, and supports soft/hard delete.
- **Suggestions & Hints:**  
  Suggests relevant discounts and provides contextual hints for stacking.
- **Audit Logging:**  
  Logs all discount applications for traceability.
- **Campaign Management:**  
  Clone and manage promotional campaigns and their discounts.
- **Extensible & Modular:**  
  Clean separation of concerns via services and validators.

---

## Key Components

- `DiscountEngine`: Orchestrates validation, stacking, application, and utility logic.
- `DiscountValidationService`: Validates codes and business rules.
- `DiscountStackingService`: Resolves which discounts can be stacked together.
- `DiscountUsageTracker`: Tracks and persists discount usage.
- `DiscountSuggestionService`: Suggests relevant discounts to users.
- `DiscountHintService`: Provides contextual hints for stacking.
- `DiscountCloningService`: Clones discounts for campaigns.
- `CodeFormatValidator`: Ensures codes are well-formed.

---

## Usage Example

```python
from discounts.services.discount_engine import DiscountEngine

final_price, applied_discounts = DiscountEngine.apply_discount_to_order(
    order=my_order,
    codes=["WELCOME10", "FREESHIP"],
    website=my_website,
    user=my_user
)
```

---

## Models

- **DiscountConfig:**
  A model for storing website-specific discount settings.
- **Discount:**  
  Represents a discount code, with fields for type, value, stacking, tiers, campaign, and more.
- **DiscountUsage:**  
  Tracks each use of a discount by a user/order.
- **DiscountStackingRule:**  
  Defines explicit stacking compatibility between discounts.
- **PromotionalCampaign:**
  Defines a promotional campaign that a discount can be linked to.

---

## Extending

- Add new validation logic in `validators/`.
- Add new stacking rules in `discount_stacking.py`.
- Add new suggestion strategies in `discount_suggestions.py`.

---

## Testing

- Unit and integration tests are recommended for all services and edge cases.
- Example: test stacking, usage limits, tiered discounts, and code format validation.

---

## Configuration

- Discount config is managed per-website via `DiscountConfigService`.
- Supports max stackable discounts, global rules, and more.

---

## License

MIT (or your license here)

---

## Authors

- Your team or company name

---

## Support

For issues, open a GitHub issue or contact the maintainers
