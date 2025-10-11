import { Button, TextField } from '@radix-ui/themes'
import { useState } from 'react'

export const LoginPanel = ({ onSubmit }: { onSubmit: Function }) => {
    const [inputText, setInputText] = useState('')

    return (
        <div>
            {' '}
            <div className="flex">
                <TextField.Root
                    placeholder="username"
                    className="mr-1"
                    value={inputText}
                    onChange={(event) => setInputText(event.target.value)}
                />
                <Button onClick={() => onSubmit(inputText)} style={{ cursor: 'pointer' }}>
                    Login
                </Button>
            </div>
            <div className="mt-1">
                Note: This test version of the game is subject to changes and data-wipes without
                warning.
            </div>
        </div>
    )
}
