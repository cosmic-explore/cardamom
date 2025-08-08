import { Box, Button, ThickCheckIcon } from '@radix-ui/themes'
import './select.css'
import {
    ActionData,
    CommandData,
    CreatureState,
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
    boxClickFunc: (data: CreatureState) => void
    updateCommand: (
        command: CommandData,
        newTarget: PositionData | null,
        action: ActionData | null
    ) => void
    setCommandMode: (commandMode: string) => void
}

export const OrderPanel = (props: OrderPanelProps) => {
    const player = getActivePlayer(props.currentPlayer.name, props.matchData)
    const creatureStates = props.matchData.creature_states.filter(
        (creatureState) => creatureState.creature.player_id === player?.id
    )

    const getCommandOfCreature = (creatureState: CreatureState) => {
        return (
            props.commands.find(
                (command: CommandData) => command.creature_state_id == creatureState.id
            ) || {
                creature_state_id: creatureState.id,
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
                {creatureStates.map((creatureState: CreatureState) => (
                    <OrderBox
                        key={creatureState.id}
                        {...{
                            creatureState,
                            commandMode: props.commandMode,
                            command: getCommandOfCreature(creatureState),
                            isSelected: props.selectedPos?.creature_state_id === creatureState.id,
                            boxClickFunc: props.boxClickFunc,
                            updateCommand: props.updateCommand,
                            setCommandMode: props.setCommandMode
                        }}
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
