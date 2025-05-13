import { CreatureData, MatchData, PlayerData } from '../DataTypes';

export type OrderPanelProps = {
    matchData: MatchData;
    currentPlayer: PlayerData;
};

export const OrderPanel = (props: OrderPanelProps) => {
    const player = getActivePlayer(props.currentPlayer.name, props.matchData);

    return (
        <div>
            <div>Orders</div>
            <div>
                {player?.creatures.map((creature: CreatureData) => {
                    return <div key={creature.id}>{creature.nickname}</div>;
                })}
            </div>
        </div>
    );
};

const getActivePlayer = (playerName: string, matchData: MatchData) => {
    if (matchData.player_1?.name == playerName) {
        return matchData.player_1;
    } else if (matchData.player_2?.name == playerName) {
        return matchData.player_2;
    }
};
