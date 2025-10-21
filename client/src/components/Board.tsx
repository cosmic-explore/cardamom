import { useEffect, useState } from 'react'
import { MatchData, PositionData } from '../DataTypes'
import { arePositionsSame, getMatchCreatureState } from '../utils/game-utils'
import { Position, PosSelectionType } from './Position'
import { getIntRange } from '../utils/general-utils'

type BoardProps = {
    matchData: MatchData
    displayedTurnNum: number
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
        displayTurn()
    }, [props.displayedTurnNum])

    useEffect(() => {
        if (props.replayingTurn === true) {
            watchTurn()
        }
    }, [props.replayingTurn])

    const displayTurn = () => {
        // display the turn from its beginning state

        if (props.displayedTurnNum === props.matchData.turn_number) {
            SetColumns(props.matchData.board.columns)
        } else {
            const initialTurnState = props.matchData.history[props.displayedTurnNum][0]
            SetColumns(initialTurnState.board.columns)
        }
    }

    const watchTurn = async () => {
        if (props.displayedTurnNum === props.matchData.turn_number) {
            // if it's the current turn, there is no history to rewatch
            props.finishReplay()
            return
        }
        const turn = props.matchData.history[props.displayedTurnNum]
        for (let i = 0; i < turn.length; i++) {
            SetColumns(turn[i].board.columns)
            await new Promise((r) => setTimeout(r, 500))
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
        // the styling of the x & y axes are similar to that of a Position component
        <div className="flex">
            <div className="flex flex-col">
                {getIntRange(columns.length).map((rowNum) => {
                    return <div className="size-12 flex justify-center items-center">{rowNum}</div>
                })}
            </div>
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
                        <div className="size-12 flex justify-center items-center">{rowIndex}</div>
                    </div>
                )
            })}
        </div>
    )
}
