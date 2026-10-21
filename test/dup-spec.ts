import symbols from '../src/symbols';
import macros from '../src/macros';
import unavailableSymbols from '../src/unavailableSymbols';

describe("Symbols and macros", () => {
    // An unavailable symbol is a macro that reports it, in place of the symbol.
    for (const macro of Object.keys(macros).filter(m => !unavailableSymbols.includes(m))) {
        it(`macro ${macro} should not shadow a symbol`, () => {
            for (const kind of Object.keys(symbols)) {
                const mode = kind as keyof typeof symbols;
                expect(symbols[mode][macro]).toBeFalsy();
            }
        });
    }
});
