
export function Layout({ form, children }) {
    return (
        <div className="flex flex-col">
            <div>
                <h1 className="text-2xl mb-5">Добро пожаловать! Введите свой город ниже что бы узнать прогноз погоды на ближайшее время</h1>
            </div>
            <div>
                {form}
            </div>
            <div>
                {children}
            </div>
        </div>
    )
}