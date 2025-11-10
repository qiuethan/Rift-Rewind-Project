import { Modal } from '@/components';
import styles from './TermsModal.module.css';

interface TermsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function TermsModal({ isOpen, onClose }: TermsModalProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Terms and Conditions">
      <div className={styles.content}>
        <h3>1. Acceptance of Terms</h3>
        <p>
          By accessing and using Heimer Academy, you accept and agree to be bound by the terms and provision of this agreement.
        </p>

        <h3>2. Use License</h3>
        <p>
          Permission is granted to temporarily access the materials (information or software) on Heimer Academy's website for personal, non-commercial transitory viewing only.
        </p>

        <h3>3. Disclaimer</h3>
        <p>
          The materials on Heimer Academy's website are provided on an 'as is' basis. Heimer Academy makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
        </p>

        <h3>4. Limitations</h3>
        <p>
          In no event shall Heimer Academy or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on Heimer Academy's website, even if Heimer Academy or a Heimer Academy authorized representative has been notified orally or in writing of the possibility of such damage.
        </p>

        <h3>5. Accuracy of Materials</h3>
        <p>
          The materials appearing on Heimer Academy's website could include technical, typographical, or photographic errors. Heimer Academy does not warrant that any of the materials on its website are accurate, complete, or current.
        </p>

        <h3>6. Links</h3>
        <p>
          Heimer Academy has not reviewed all of the sites linked to its website and is not responsible for the contents of any such linked site. The inclusion of any link does not imply endorsement by Heimer Academy of the site.
        </p>

        <h3>7. Modifications</h3>
        <p>
          Heimer Academy may revise these terms of service for its website at any time without notice. By using this website you are agreeing to be bound by the then current version of these terms of service.
        </p>

        <h3>8. Governing Law</h3>
        <p>
          These terms and conditions are governed by and construed in accordance with the laws of your jurisdiction and you irrevocably submit to the exclusive jurisdiction of the courts in that state or location.
        </p>
      </div>
    </Modal>
  );
}