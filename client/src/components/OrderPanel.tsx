import { Box, Button, ThickCheckIcon } from '@radix-ui/themes'
import './select.css'
import {
    ActionData,
    CommandData,
    CreatureData,
    MatchData,
    PlayerData,
    PositionData
} from '../DataTypes'
import { OrderBox } from './OrderBox'
import { getActivePlayer } from '../utils/game-utils'
import { submitMatchCommands } from '../utils/server-connection'

export type OrderPanelProps = {
    matchData: MatchData
    currentPlayer: PlayerData
    commandMode: string
    commands: CommandData[]
    submitted: boolean
    selectedPos: PositionData | null
    boxClickFunc: (data: CreatureData) => void
    updateCommand: (
        command: CommandData,
        newTarget: PositionData | null,
        action: ActionData | null
    ) => void
    setCommandMode: (commandMode: string) => void
}

export const OrderPanel = (props: OrderPanelProps) => {
    const player = getActivePlayer(props.currentPlayer.name, props.matchData)

    const getCommandOfCreature = (creature: CreatureData) => {
        return (
            props.commands.find((command: CommandData) => command.creature.id == creature.id) || {
                creature: creature,
                move_target: null,
                action: null,
                action_target: null
            }
        )
    }

    const handleCommandSubmission = () => {
        submitMatchCommands(props.commands)
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
                            isSelected: props.selectedPos?.creature_id === creature.id,
                            boxClickFunc: props.boxClickFunc,
                            updateCommand: props.updateCommand,
                            setCommandMode: props.setCommandMode
                        }}
                        key={creature.id}
                    />
                ))}
            </Box>
            <div className="flex flex-row mt-3">
                <Button style={{ cursor: 'pointer' }} onClick={() => handleCommandSubmission()}>
                    Submit
                </Button>
                {props.submitted ? (
                    <div className="text-green-600">
                        <ThickCheckIcon />
                    </div>
                ) : (
                    ''
                )}
            </div>
        </Box>
    )
}
