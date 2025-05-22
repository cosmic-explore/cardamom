import { Box, Flex } from '@radix-ui/themes'
import { Select } from 'radix-ui'

import { CommandData, CreatureData } from '../DataTypes'

export type OrderBoxProps = {
    creature: CreatureData
    commandMode: string
    command: CommandData | undefined
    isSelected: boolean
    boxClickFunc: (data: CreatureData) => void
    setCommandMode: (commandMode: string) => void
}

export const OrderBox = (props: OrderBoxProps) => {
    const moveBorderStyle = props.isSelected && props.commandMode === 'move' ? 'border' : ''
    const actionBorderStyle = props.isSelected && props.commandMode === 'action' ? 'border' : ''

    return (
        <Box
            className={`border p-5 ${props.isSelected ? 'bg-yellow-100' : ''}`}
            onClick={() => props.boxClickFunc(props.creature)}
        >
            <Flex>
                <Box className="mr-5">{props.creature.nickname}</Box>
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
                            <Select.Root>
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
                                        {props.creature.actions.map((action) => {
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
