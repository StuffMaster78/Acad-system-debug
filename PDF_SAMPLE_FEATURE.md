# PDF Sample Download Feature

## Overview

This feature allows blog posts and service pages to include downloadable PDF samples organized in sections. Users can download these PDFs, and the system tracks downloads for analytics.

## ✅ Implemented Features

### 1. **Blog PDF Samples** ✅
- ✅ `PDFSampleSection` model - Sections for organizing PDFs
- ✅ `PDFSample` model - Individual PDF files
- ✅ `PDFSampleDownload` model - Download tracking
- ✅ File size auto-calculation
- ✅ Download counter
- ✅ Authentication requirements per section
- ✅ Featured PDFs
- ✅ Display ordering

### 2. **Service Page PDF Samples** ✅
- ✅ `ServicePagePDFSampleSection` model
- ✅ `ServicePagePDFSample` model
- ✅ `ServicePagePDFSampleDownload` model
- ✅ Same features as blog PDFs

### 3. **API Endpoints** ✅
- ✅ `GET /api/v1/blog/pdf-sample-sections/` - List sections
- ✅ `POST /api/v1/blog/pdf-sample-sections/` - Create section
- ✅ `GET /api/v1/blog/pdf-samples/` - List PDFs
- ✅ `POST /api/v1/blog/pdf-samples/` - Upload PDF
- ✅ `GET /api/v1/blog/pdf-samples/{id}/download/` - Download PDF
- ✅ `GET /api/v1/blog/pdf-samples/popular/` - Most downloaded
- ✅ `GET /api/v1/blog/pdf-sample-downloads/` - View downloads
- ✅ `GET /api/v1/blog/pdf-sample-downloads/stats/` - Download statistics

### 4. **Admin Interface** ✅
- ✅ Admin for PDF sections
- ✅ Admin for PDF samples with file size display
- ✅ Admin for download tracking
- ✅ Admin actions (reset download count)
- ✅ Filtering and search

### 5. **Security Features** ✅
- ✅ PDF file validation (only PDFs allowed)
- ✅ Optional authentication requirement
- ✅ IP address and user tracking
- ✅ Download analytics

## Models

### PDFSampleSection (Blog)
```python
- blog: ForeignKey to BlogPost
- title: Section title
- description: Section description
- display_order: Order for display
- is_active: Visibility toggle
- requires_auth: Require login to download
```

### PDFSample (Blog)
```python
- section: ForeignKey to PDFSampleSection
- title: PDF display name
- description: PDF description
- pdf_file: FileField (PDF only, max 10MB)
- file_size: Auto-calculated file size
- display_order: Display order
- download_count: Download counter
- is_featured: Featured flag
- is_active: Active flag
- uploaded_by: User who uploaded
```

### PDFSampleDownload (Blog)
```python
- pdf_sample: ForeignKey to PDFSample
- user: User who downloaded (optional)
- ip_address: IP address
- user_agent: Browser info
- session_id: Session tracking
- downloaded_at: Timestamp
```

## Usage Examples

### Creating a PDF Section
```python
from blog_pages_management.models.pdf_samples import PDFSampleSection

section = PDFSampleSection.objects.create(
    blog=blog_post,
    title="Sample Reports",
    description="Download our sample reports",
    display_order=1,
    requires_auth=False
)
```

### Uploading a PDF
```python
from blog_pages_management.models.pdf_samples import PDFSample

pdf = PDFSample.objects.create(
    section=section,
    title="Annual Report 2024",
    description="Our annual report for 2024",
    pdf_file=uploaded_file,  # File object
    display_order=1,
    is_featured=True,
    uploaded_by=request.user
)
```

### Downloading a PDF via API
```
GET /api/v1/blog/pdf-samples/{id}/download/
```

Returns the PDF file with proper headers for download.

### Getting Download Statistics
```python
# Via API
GET /api/v1/blog/pdf-sample-downloads/stats/?pdf_id=1

# Returns:
{
    "total_downloads": 150,
    "unique_users": 45,
    "unique_ips": 120
}
```

### Getting Popular PDFs
```
GET /api/v1/blog/pdf-samples/popular/?limit=5
```

Returns the most downloaded PDFs.

## Frontend Integration

### Display PDF Sections
```html
{% for section in blog.pdf_sample_sections.all %}
    <div class="pdf-section">
        <h3>{{ section.title }}</h3>
        <p>{{ section.description }}</p>
        
        {% for pdf in section.pdf_samples.all %}
            <div class="pdf-item">
                <h4>{{ pdf.title }}</h4>
                <p>{{ pdf.description }}</p>
                <p>Size: {{ pdf.file_size_human }}</p>
                <p>Downloads: {{ pdf.download_count }}</p>
                <a href="/api/v1/blog/pdf-samples/{{ pdf.id }}/download/" 
                   class="download-btn">
                    Download PDF
                </a>
            </div>
        {% endfor %}
    </div>
{% endfor %}
```

### JavaScript Download Tracking
```javascript
// Track download with AJAX before triggering download
function downloadPDF(pdfId) {
    fetch(`/api/v1/blog/pdf-samples/${pdfId}/download/`, {
        method: 'GET',
        credentials: 'include'
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Download failed');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sample-${pdfId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Download error:', error);
        alert('Failed to download PDF. Please try again.');
    });
}
```

## Admin Interface

### PDF Sample Section Admin
- List view shows: Title, Blog, Display Order, Active Status, PDF Count
- Filters: Active status, Requires auth, Website
- Search: Title, Description, Blog title

### PDF Sample Admin
- List view shows: Title, Section, File Size, Download Count, Featured, Active
- Filters: Active, Featured, Website, Created date
- Fieldsets: Basic Info, Display, Analytics, Metadata
- Actions: Reset download count

### Download Tracking Admin
- List view shows: PDF, User, IP Address, Download Time
- Filters: Download date, Website
- Search: PDF title, Username, IP address
- Downloads are auto-created (no manual add permission)

## Security Considerations

1. **File Validation**: Only PDF files are allowed (enforced by `FileExtensionValidator`)
2. **File Size**: Consider adding a file size limit (recommend max 10MB)
3. **Authentication**: Sections can require authentication for downloads
4. **Access Control**: Admin-only upload, public or authenticated downloads
5. **Rate Limiting**: Consider adding rate limiting for downloads to prevent abuse

## Analytics

### Available Metrics
- Total downloads per PDF
- Unique users who downloaded
- Unique IP addresses
- Download trends over time
- Most popular PDFs
- Downloads per blog/service page

### Accessing Analytics
```python
# Get stats for a specific PDF
stats = PDFSampleDownload.objects.filter(pdf_sample_id=1).aggregate(
    total=Count('id'),
    unique_users=Count('user', distinct=True),
    unique_ips=Count('ip_address', distinct=True)
)

# Get stats for all PDFs in a blog
blog_pdfs = PDFSample.objects.filter(section__blog_id=1)
total_downloads = PDFSampleDownload.objects.filter(
    pdf_sample__in=blog_pdfs
).count()
```

## Migration Instructions

1. **Create Migrations**:
```bash
python manage.py makemigrations blog_pages_management
python manage.py makemigrations service_pages_management
```

2. **Run Migrations**:
```bash
python manage.py migrate blog_pages_management
python manage.py migrate service_pages_management
```

## Testing Checklist

- [ ] Create PDF sample section for blog
- [ ] Upload PDF to section
- [ ] Download PDF (anonymous user)
- [ ] Download PDF (authenticated user)
- [ ] Test authentication requirement
- [ ] Verify download tracking
- [ ] Check download counter increment
- [ ] View download statistics
- [ ] Get popular PDFs
- [ ] Test admin interface
- [ ] Test file size calculation
- [ ] Test file validation (non-PDF files)
- [ ] Test service page PDF samples
- [ ] Test download analytics

## Future Enhancements

1. **File Size Limits**: Add configurable file size limits
2. **Virus Scanning**: Integrate virus scanning for uploads
3. **Expiration Dates**: Add expiration dates for PDFs
4. **Download Limits**: Per-user download limits
5. **Email Capture**: Optional email capture before download
6. **Preview**: PDF preview before download
7. **Watermarking**: Add watermarks to downloaded PDFs
8. **CDN Integration**: Serve PDFs from CDN
9. **Compression**: Auto-compress large PDFs
10. **Categories**: Categorize PDFs within sections

