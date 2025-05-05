import { useState } from "react";
import { MatchData, PlayerData, PositionData } from "../DataTypes";
import { Board } from "./Board";
import { Button } from "@radix-ui/themes";
import { OrderPanel } from "./OrderPanel";
import { DetailPanel } from "./DetailPanel";
import { getCreatureMoves, refreshMatch } from "../utils/server-connection";

export const MatchPanel = (props : {matchData: MatchData, playerData: PlayerData}) => {
    const [selectedPos, setSelectedPos] = useState<PositionData | null>(null)
    const [highlightedPosList, setHighlightedPosList] = useState<PositionData[]>([])

    const handleRefreshMatch = () => {
        refreshMatch()
    }

    const handlePosClick = async (posData: PositionData) => {
        setSelectedPos(posData)
        if (posData.creature !== null) {
            // ask the server for the possible moves
            let response = await getCreatureMoves(posData.creature.nickname)
            setHighlightedPosList(response)
        } else {
            setHighlightedPosList([])
        }
    }

    return (
        <div className="flex flex-row">
            <div className="flex flex-col items-center">
                <div className='mb-1'>{props.matchData.id}</div>
                <div className="flex flex-row mb-3">
                    <div>Player 1: {props.matchData.player_1?.name}</div>
                    <div className="pl-8 pr-8"/>
                    <div>Player 2: {props.matchData.player_2?.name}</div>
                </div>
                <Board {...{
                    boardData: props.matchData.board,
                    selectedPos,
                    highlightedPosList,
                    handlePosClick
                }}/>
            </div>
            <div className='flex flex-col grow-1 items-center'>
                <div className='flex flex-row'>
                    {selectedPos ? <DetailPanel {...selectedPos}/> : ''}
                    {
                        props.playerData && props.matchData ? 
                        <OrderPanel {...{currentPlayer: props.playerData, matchData: props.matchData}}/>
                        : ''
                    }
                </div>
                <Button onClick={handleRefreshMatch}>Refresh Match Data</Button>
            </div>
        </div>
    )
}