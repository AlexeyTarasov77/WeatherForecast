/**
 *
 * @param {{
 *  width: 'md' | 'full',
 *  className: string,
 *  isOpen: boolean
 * }} props
 * @returns
 */

import clsx from "clsx";
import { createPortal } from "react-dom";

export function UiModal({ width = "md", className, children, isOpen = false, onClose }) {

  const handleClick = (event) => {
    if (!event.target.closest('[data-id="modal"]')) {
        onClose();
    }
  };

  if (!isOpen) return null

  const modal = (
    <div className={clsx("fixed inset-0 bg-slate-900/60 backdrop-blur overflow-y-auto", className)} onClick={handleClick}>
      <div
        className={clsx(
          "flex flex-col rounded-lg min-h-80 bg-white mt-12 shadow-md mx-auto relative",
          {
            md: "max-w-[640px] w-full",
            full: "mx-5",
          }[width]
        )}
        data-id="modal"
      >
        <button className="
            py-1 px-2 flex justify-center
            items-center bg-white/10 rounded w-8 h-8
            backdrop-blur absolute top-0 left-[calc(100%+12px)]
            transition-colors hover:bg-white/40 "
            onClick={onClose}
            data-id="close-modal">
          <CrossLightIcon className={"w-4 h-4 text-white"} />
        </button>
        { children }
      </div>
    </div>
  );
  return createPortal(modal, document.getElementById("modals"));
}

UiModal.Header = function UiModalHeader({ children, className }) {
    return (
        <div className={clsx("px-6 pt-4 pb-4 text-2xl", className)}>{children}</div>
    )
}

UiModal.Body = function UiModalBody({ children, className }) {
    return (
        <div className={clsx(className, "px-6")}>{children}</div>
    )
}

UiModal.Footer = function UiModalFooter({ children, className }) {
    return (
        <div className={clsx(className, "p-6 flex gap-4 justify-end mt-auto")}>{children}</div>
    )
}
function CrossLightIcon({ className }) {
  return (
    <svg
      className={className}
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M0.781152 16C0.626614 16 0.475539 15.9542 0.347036 15.8684C0.218534 15.7825 0.118376 15.6605 0.0592335 15.5177C9.05196e-05 15.3749 -0.0153811 15.2178 0.0147757 15.0663C0.0449324 14.9147 0.119363 14.7755 0.228652 14.6662L14.6662 0.228731C14.8127 0.0821988 15.0114 -0.00012207 15.2187 -0.00012207C15.4259 -0.00012207 15.6246 0.0821988 15.7712 0.228731C15.9177 0.375263 16 0.574003 16 0.781231C16 0.988459 15.9177 1.1872 15.7712 1.33373L1.33365 15.7712C1.26116 15.8439 1.17504 15.9015 1.08022 15.9407C0.985408 15.98 0.883772 16.0001 0.781152 16Z"
        fill="currentColor"
      />
      <path
        d="M15.2187 16C15.116 16.0001 15.0144 15.98 14.9196 15.9407C14.8248 15.9015 14.7386 15.8439 14.6662 15.7712L0.228652 1.33373C0.0821198 1.1872 -0.000201104 0.988459 -0.000201104 0.781231C-0.000201104 0.574003 0.0821198 0.375263 0.228652 0.228731C0.375184 0.0821988 0.573924 -0.00012207 0.781152 -0.00012207C0.98838 -0.00012207 1.18712 0.0821988 1.33365 0.228731L15.7712 14.6662C15.8804 14.7755 15.9549 14.9147 15.985 15.0663C16.0152 15.2178 15.9997 15.3749 15.9406 15.5177C15.8814 15.6605 15.7813 15.7825 15.6528 15.8684C15.5243 15.9542 15.3732 16 15.2187 16Z"
        fill="currentColor"
      />
    </svg>
  );
}
