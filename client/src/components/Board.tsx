import { useEffect, useState } from 'react'
import { MatchData, PositionData } from '../DataTypes'
import { arePositionsSame, getMatchCreatureState } from '../utils/game-utils'
import { Position, PosSelectionType } from './Position'

type BoardProps = {
    matchData: MatchData
    selectedPos: PositionData | null
    highlightedPosList: PositionData[]
    handlePosClick: (data: PositionData) => void
    getTargetedPos: () => PositionData | null
    replayingTurn: boolean
    finishReplay: () => void
}

export function Board(props: BoardProps) {
    const [columns, SetColumns] = useState<PositionData[][]>(props.matchData.board.columns)

    useEffect(() => {
        SetColumns(props.matchData.board.columns)
    }, [props.matchData])

    useEffect(() => {
        if (props.replayingTurn === true) {
            watchTurn()
        } else {
            SetColumns(props.matchData.board.columns)
        }
    }, [props.replayingTurn])

    const watchTurn = async () => {
        // the previous turn (whose outcome is the current board state) will be
        // the current turn_number - 1
        const turn = props.matchData.history[props.matchData.turn_number - 1]
        for (let i = 0; i < turn.length; i++) {
            SetColumns(turn[i].board.columns)
            await new Promise((r) => setTimeout(r, 200))
        }
        props.finishReplay()
    }

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
                                            creatureState: posData.creature_state_id
                                                ? getMatchCreatureState(
                                                      props.matchData,
                                                      posData.creature_state_id
                                                  )
                                                : null,
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
