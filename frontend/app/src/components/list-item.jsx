import clsx from "clsx"

export function ListItem({ children, onClick, className }) {
    return (
        <li className={clsx(className, "border-b transition-colors p-2 rounded hover:bg-slate-300")}>
            <button className="bg-transparent w-full h-full border-none border-0 flex items-center justify-start" onClick={onClick}>
                {children}
            </button>
        </li>
    )
}