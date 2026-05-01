import { useEffect } from 'react';

/**
 * Predictify — SEO Head Component (F6)
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
    document.title = `${title} | Predictify`;

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
      'og:title': `${title} | Predictify`,
      'og:description': description || 'AI-Powered Software Project Cost & Timeline Estimation',
      'og:type': 'website',
      'og:site_name': 'Predictify',
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
      document.title = 'Predictify — Smart Project Estimation';
    };
  }, [title, description]);

  return null; // This component only manages <head>, no visible UI
}
