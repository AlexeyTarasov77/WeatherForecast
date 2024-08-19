import clsx from "clsx";


export function UiFieldInput({ required, className, errorText, ...inputProps }) {
    return (
      <input
        required={required}
        id="example2"
        className={clsx(
          `block w-full rounded-md shadow-md focus:ring
          focus:ring-opacity-50 disabled:cursor-not-allowed
          disabled:bg-gray-50 disabled:text-slate-400 p-3`,
          errorText
            ? "border-red-500 focus:border-red-300 focus:ring-red-200"
            : "border-slate-300 focus:border-teal-600 focus:ring-teal-300",
          className
        )}
        {...inputProps}
      />
    );
  }