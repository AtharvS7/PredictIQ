import { useEffect } from 'react';

/**
 * PredictIQ — SEO Head Component
 * Sets document title and meta description for each page.
 * Lightweight alternative to react-helmet — no extra dependency needed.
 */
interface SEOHeadProps {
  title: string;
  description?: string;
}

export default function SEOHead({ title, description }: SEOHeadProps) {
  useEffect(() => {
    // Set page title
    document.title = `${title} | PredictIQ`;

    // Set meta description
    if (description) {
      let metaDesc = document.querySelector('meta[name="description"]');
      if (!metaDesc) {
        metaDesc = document.createElement('meta');
        metaDesc.setAttribute('name', 'description');
        document.head.appendChild(metaDesc);
      }
      metaDesc.setAttribute('content', description);
    }

    // Set Open Graph tags for social sharing
    const ogTags: Record<string, string> = {
      'og:title': `${title} | PredictIQ`,
      'og:description': description || 'PredictIQ Enterprise Software Project Effort and Budget Estimation',
      'og:type': 'website',
      'og:site_name': 'PredictIQ',
    };

    Object.entries(ogTags).forEach(([property, content]) => {
      let tag = document.querySelector(`meta[property="${property}"]`);
      if (!tag) {
        tag = document.createElement('meta');
        tag.setAttribute('property', property);
        document.head.appendChild(tag);
      }
      tag.setAttribute('content', content);
    });

    return () => {
      // Reset to default on unmount
      document.title = 'PredictIQ — Software Project Estimation';
    };
  }, [title, description]);

  return null; // This component only manages <head>, no visible UI
}
