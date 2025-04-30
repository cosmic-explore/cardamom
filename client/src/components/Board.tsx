import { BoardData, PositionData } from "../DataTypes"
import { Position, PosSelectionType } from "./Position"

type BoardProps = {
    boardData: BoardData
    selectedPos: PositionData | null
    handlePosClick: (data: PositionData) => void
}

export function Board(props : BoardProps) {
    const columns = props.boardData.columns
    
    return (
        <div className="flex">
           {columns.map((col, rowIndex: number) => {
                return (
                <div key={rowIndex}>
                    {col.map((posData : PositionData, colIndex : number) => {
                        let selection = PosSelectionType.none
                        if (props.selectedPos?.x === rowIndex && props.selectedPos.y === colIndex) {
                            selection = PosSelectionType.selected
                        }
                        return (
                            <div key={`${rowIndex},${colIndex}`}>
                                <Position {...{
                                    posData,
                                    selection,
                                    clickFunc: props.handlePosClick
                                }}/>
                            </div>
                        )}
                    )}
                </div>
                )
            })}
      </div>
    )
}