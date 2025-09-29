import { CreatureState, PositionData } from '../DataTypes'
import { GameSprite } from './GameSprite'

export enum PosSelectionType {
    // values are Tailwind.css classnames for styling
    none = 'bg-orange-100',
    selected = 'bg-sky-100',
    highlighted = 'bg-cyan-100',
    targeted = 'bg-green-100'
}

export type PositionProps = {
    posData: PositionData
    creatureState: CreatureState | null
    selectionType: PosSelectionType
    clickFunc: (data: PositionData) => void
}

export function Position(props: PositionProps) {
    const handleClick = () => {
        props.clickFunc(props.posData)
    }

    const showCoords = props.posData.effects.length == 0 && props.creatureState == null

    return (
        <div
            className={`${props.selectionType} size-12 outline hover:bg-sky-100 flex justify-center items-center`}
            onClick={handleClick}
            style={{ cursor: 'pointer' }}
        >
            {props.posData.effects.length > 0 ? (
                <GameSprite {...{ spriteName: 'Action Effect' }} />
            ) : (
                ''
            )}
            {props.creatureState != null ? (
                <GameSprite {...{ spriteName: props.creatureState.creature.species.name }} />
            ) : (
                ''
            )}
            {showCoords ? `${props.posData.x},${props.posData.y}` : ''}
        </div>
    )
}
