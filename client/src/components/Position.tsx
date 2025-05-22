import { PositionData } from '../DataTypes'
import { CreatureIcon } from './CreatureSprite'

export enum PosSelectionType {
    // values are Tailwind.css classnames for styling
    none = 'bg-orange-100',
    selected = 'bg-sky-100',
    highlighted = 'bg-cyan-100',
    targeted = 'bg-green-100'
}

export type PositionProps = {
    posData: PositionData
    selectionType: PosSelectionType
    clickFunc: (data: PositionData) => void
}

export function Position(props: PositionProps) {
    const handleClick = () => {
        props.clickFunc(props.posData)
    }

    return (
        <div
            className={`${props.selectionType} size-12 outline hover:bg-sky-100 flex justify-center items-center`}
            onClick={handleClick}
            style={{ cursor: 'pointer' }}
        >
            {props.posData.creature ? (
                <CreatureIcon {...{ speciesName: props.posData.creature.nickname }} />
            ) : (
                `${props.posData.x},${props.posData.y}`
            )}
        </div>
    )
}
