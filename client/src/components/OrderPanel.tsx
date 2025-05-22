import { CommandData, CreatureData, MatchData, PlayerData } from "../DataTypes"
import { Select } from "radix-ui";

export type OrderPanelProps = {
    matchData: MatchData
    currentPlayer: PlayerData
    commands: CommandData[]
}

export const OrderPanel = (props: OrderPanelProps) => {
    const player = getActivePlayer(props.currentPlayer.name, props.matchData);

    const getCommandOfCreature = (creature: CreatureData) => {
        return props.commands.find((command : CommandData) => command.creature.nickname == creature.nickname])
    }

    return (
        <div>
            <div className="border">Orders</div>
            <div>
                {player?.creatures.map((creature: CreatureData) => {
                    const command = getCommandOfCreature(creature)
                    return (
                        <div key={creature.id} className="border p-5">
                            {creature.nickname}
                            <div>
                                <div>Move</div>
                                {command?.move_target?.x},{command?.move_target?.y}
                            </div>
                            <div>
                                <div>Action</div>
                                <div>
                                    <Select.Root>
                                        <Select.Portal>
                                            <Select.Content>
                                                {creature.actions.map((action => {
                                                    return ( 
                                                        <Select.Item value={action.name} key={action.name}>
                                                            {action.name}
                                                        </Select.Item>
                                                    )
                                                }))}
                                            </Select.Content>
                                        </Select.Portal>
                                    </Select.Root>
                                    
                                </div>
                            </div>
                        </div>
                    ) 
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
