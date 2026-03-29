# Missing Migrations - Created Manually

## Status: In Progress

The following migrations have been created manually based on Django's `makemigrations --dry-run` output:

### ✅ Completed

1. **discounts/0003_seasonalevent.py** - Create proxy model SeasonalEvent
2. **order_configs/0004_alter_englishtype_code_alter_englishtype_name_and_more.py** - Field alterations

### ⏳ Remaining to Create

3. **order_payments_management/0010_discountusage_alter_invoice_options_and_more.py**
   - Create proxy model DiscountUsage
   - Change Meta options on invoice
   - Rename indexes (Django auto-generates different names)
   - Alter various fields

4. **orders/0007_rename_orders_order_status_idx...**
   - Rename indexes (Django auto-generates different names)
   - Alter unique_together for writerprogress
   - Alter field notes, progress_percentage on writerprogress

5. **refunds/0002_alter_refund_order_payment_alter_refund_processed_by.py**
   - Alter field order_payment on refund
   - Alter field processed_by on refund

6. **reviews_system/0002_alter_orderreview_reviewer_and_more.py**
   - Alter field reviewer on orderreview, websitereview, writerreview

7. **service_pages_management/0004_servicepagecta_servicepageedithistory_servicepagefaq_and_more.py**
   - Create models: ServicePageCTA, ServicePageEditHistory, ServicePageFAQ, ServicePageResource, ServicePageSEOMetadata
   - Rename indexes
   - Add fields to new models

8. **special_orders/0003_installmentpayment_payment_record_and_more.py**
   - Add field payment_record to installmentpayment
   - Alter field special_order on writerbonus

9. **communications** (details cut off in output)

## Note on Index Renames

Django is detecting that manually created indexes have different names than what Django would auto-generate. The index renames are safe - they're just updating the names to match Django's naming convention.

## Next Steps

1. Apply the completed migrations
2. Create the remaining migrations manually
3. Or run `makemigrations` to auto-generate them and review

