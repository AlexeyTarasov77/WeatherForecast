

export function Root() {
    return (
        <div className="flex flex-col items-center mt-10">
            <h1 className="text-3xl font-bold font-mono">Welcome!</h1>
            <p className="text-lg text-slate-500">To get started, visit a <a className="underline text-emerald-600" href="/forecast/daily">daily forecast</a></p>
        </div>
    )
}