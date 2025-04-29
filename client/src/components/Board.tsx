import { BoardData, PositionData } from "../DataTypes"
import { Position } from "./Position"


export function Board(props : BoardData) {  
    return (
        <div className="flex">
           {props.columns.map((col, colIndex: number) => {
                return (
                <div key={colIndex}>
                    {col.map((pos : PositionData, rowIndex : number) => {
                        return (
                            <div key={`${rowIndex},${colIndex}`}>
                                <Position {...pos}/>
                            </div>
                        )}
                    )}
                </div>
                )
            })}
      </div>
    )
}