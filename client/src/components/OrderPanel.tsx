import { Box, Button } from '@radix-ui/themes'
import {
    ActionData,
    CommandData,
    CreatureData,
    MatchData,
    PlayerData,
    PositionData
} from '../DataTypes'
import './select.css'
import { OrderBox } from './OrderBox'

export type OrderPanelProps = {
    matchData: MatchData
    currentPlayer: PlayerData
    commandMode: string
    currentAction: ActionData | null
    commands: CommandData[]
    selectedPos: PositionData | null
    boxClickFunc: (data: CreatureData) => void
    setCommandMode: (commandMode: string) => void
    setCurrentAction: (action: ActionData | null) => void
}

export const OrderPanel = (props: OrderPanelProps) => {
    const player = getActivePlayer(props.currentPlayer.name, props.matchData)

    const getCommandOfCreature = (creature: CreatureData) => {
        return props.commands.find(
            (command: CommandData) => command.creature.nickname == creature.nickname
        )
    }

    return (
        <Box className="border p-1 w-100">
            <div>Your Orders</div>
            <Box>
                {player?.creatures.map((creature: CreatureData) => (
                    <OrderBox
                        {...{
                            creature,
                            commandMode: props.commandMode,
                            command: getCommandOfCreature(creature),
                            currentAction: props.currentAction,
                            isSelected: props.selectedPos?.creature?.nickname === creature.nickname,
                            boxClickFunc: props.boxClickFunc,
                            setCommandMode: props.setCommandMode,
                            setCurrentAction: props.setCurrentAction
                        }}
                        key={creature.id}
                    />
                ))}
            </Box>
            <Button>Submit</Button>
        </Box>
    )
}

const getActivePlayer = (playerName: string, matchData: MatchData) => {
    if (matchData.player_1?.name == playerName) {
        return matchData.player_1
    } else if (matchData.player_2?.name == playerName) {
        return matchData.player_2
    }
}
