// src/components/Footer.tsx
import Link from 'next/link';

export const Footer = () => {
  return (
    <footer className="bg-gray-50 border-t">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Course Companion</h3>
            <p className="text-gray-600 text-sm">
              Master AI Agent Development with our comprehensive course covering Claude Agent SDK, 
              MCP integration, and production deployment patterns.
            </p>
          </div>
          
          <div>
            <h4 className="font-medium mb-4">Courses</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/modules" className="hover:text-blue-600">All Modules</Link></li>
              <li><Link href="/chapters" className="hover:text-blue-600">Chapters</Link></li>
              <li><Link href="/quizzes" className="hover:text-blue-600">Quizzes</Link></li>
              <li><Link href="/resources" className="hover:text-blue-600">Resources</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4">Support</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/help" className="hover:text-blue-600">Help Center</Link></li>
              <li><Link href="/faq" className="hover:text-blue-600">FAQ</Link></li>
              <li><Link href="/contact" className="hover:text-blue-600">Contact Us</Link></li>
              <li><Link href="/community" className="hover:text-blue-600">Community</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-medium mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/terms" className="hover:text-blue-600">Terms of Service</Link></li>
              <li><Link href="/privacy" className="hover:text-blue-600">Privacy Policy</Link></li>
              <li><Link href="/cookies" className="hover:text-blue-600">Cookie Policy</Link></li>
              <li><Link href="/licenses" className="hover:text-blue-600">Licenses</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t mt-8 pt-8 text-center text-sm text-gray-600">
          <p>© {new Date().getFullYear()} Course Companion. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};