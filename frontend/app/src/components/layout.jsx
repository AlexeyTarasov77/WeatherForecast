
export function Layout({ form, children, modal }) {
    return (
        <div>
            <div>
                {modal}
            </div>
            <div className="flex flex-col p-5">
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
        </div>
    )
}