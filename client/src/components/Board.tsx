import { BoardData, PositionData } from '../DataTypes'
import { arePositionsSame } from '../utils/game-utils'
import { Position, PosSelectionType } from './Position'

type BoardProps = {
    boardData: BoardData
    selectedPos: PositionData | null
    highlightedPosList: PositionData[]
    handlePosClick: (data: PositionData) => void
    getTargetedPos: () => PositionData | null
}

export function Board(props: BoardProps) {
    const columns = props.boardData.columns

    const getSelectionType = (posData: PositionData): PosSelectionType => {
        const targetedPos = props.getTargetedPos()

        if (props.selectedPos && arePositionsSame(props.selectedPos, posData)) {
            return PosSelectionType.selected
        } else if (targetedPos && arePositionsSame(targetedPos, posData)) {
            return PosSelectionType.targeted
        } else if (
            props.highlightedPosList.some((highlightedPos) =>
                arePositionsSame(highlightedPos, posData)
            )
        ) {
            return PosSelectionType.highlighted
        } else {
            return PosSelectionType.none
        }
    }

    return (
        <div className="flex">
            {columns.map((col, rowIndex: number) => {
                return (
                    <div key={rowIndex}>
                        {col.map((posData: PositionData, colIndex: number) => {
                            const selectionType = getSelectionType(posData)
                            return (
                                <div key={`${rowIndex},${colIndex}`}>
                                    <Position
                                        {...{
                                            posData,
                                            selectionType,
                                            clickFunc: props.handlePosClick
                                        }}
                                    />
                                </div>
                            )
                        })}
                    </div>
                )
            })}
        </div>
    )
}
