import { MatchData } from "../DataTypes";
import { Board } from "./Board";

export const MatchPanel = (props : MatchData) => {
    return (
        <div className="flex flex-col items-center">
            <div className='mb-1'>{props.id}</div>
            <div className="flex flex-row mb-3">
                <div>Player 1: {props.player_1?.name}</div>
                <div className="pl-8 pr-8"/>
                <div>Player 2: {props.player_2?.name}</div>
            </div>
            <Board {...props.board}/>
        </div>
    )
}