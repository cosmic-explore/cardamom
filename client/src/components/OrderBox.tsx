import { Box, Flex } from '@radix-ui/themes'
import { Select } from 'radix-ui'
import { ActionData, CommandData, CreatureState, PositionData } from '../DataTypes'

export type OrderBoxProps = {
    creatureState: CreatureState
    commandMode: string
    command: CommandData
    isSelected: boolean
    boxClickFunc: (data: CreatureState) => void
    updateCommand: (
        command: CommandData,
        newTarget: PositionData | null,
        action: ActionData | null
    ) => void
    setCommandMode: (commandMode: string) => void
}

export const OrderBox = (props: OrderBoxProps) => {
    const moveBorderStyle = props.isSelected && props.commandMode === 'move' ? 'border' : ''
    const actionBorderStyle = props.isSelected && props.commandMode === 'action' ? 'border' : ''

    const handleActionChange = (actionName: string) => {
        const newAction =
            props.creatureState.creature.actions.find((a) => a.name === actionName) || null
        props.updateCommand(props.command, null, newAction)
    }

    return (
        <Box
            className={`border p-5 ${props.isSelected ? 'bg-yellow-100' : ''}`}
            onClick={() => props.boxClickFunc(props.creatureState)}
        >
            <Flex>
                <Box className="mr-5">{props.creatureState.creature.nickname}</Box>
                <Box>
                    <div
                        className={`flex w-100 ${moveBorderStyle}`}
                        onClick={() => props.setCommandMode('move')}
                    >
                        <div className="mr-1">Move</div>
                        {props.command?.move_target?.x},{props.command?.move_target?.y}
                    </div>
                    <div
                        className={`flex w-100 ${actionBorderStyle}`}
                        onClick={() => props.setCommandMode('action')}
                    >
                        <div className="mr-1">Action</div>
                        <Box>
                            <Select.Root
                                value={props.command.action?.name || 'None'}
                                onValueChange={(value) => handleActionChange(value)}
                            >
                                <Select.Trigger
                                    className="SelectTrigger"
                                    style={{ cursor: 'pointer' }}
                                >
                                    <Select.Value placeholder="None" />
                                </Select.Trigger>
                                <Select.Content className="SelectContent">
                                    <Select.Viewport className="SelectViewport">
                                        <Select.Item value="None" style={{ cursor: 'pointer' }}>
                                            <Select.ItemText>None</Select.ItemText>
                                        </Select.Item>
                                        <Select.Separator />
                                        {props.creatureState.creature.actions.map((action) => {
                                            return (
                                                <Select.Item
                                                    value={action.name}
                                                    key={action.name}
                                                    style={{ cursor: 'pointer' }}
                                                >
                                                    <Select.ItemText>{action.name}</Select.ItemText>
                                                </Select.Item>
                                            )
                                        })}
                                    </Select.Viewport>
                                </Select.Content>
                            </Select.Root>
                        </Box>
                        <div>
                            {props.command?.action_target?.x},{props.command?.action_target?.y}
                        </div>
                    </div>
                </Box>
            </Flex>
        </Box>
    )
}
