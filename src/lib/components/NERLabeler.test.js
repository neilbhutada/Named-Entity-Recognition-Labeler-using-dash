import React from 'react';
import renderer, { act } from 'react-test-renderer';
import NERLabeler from './NERLabeler.react';

test('adds entity on label selection', () => {
  const mockSetProps = jest.fn();
  const component = renderer.create(<NERLabeler text="Hello world" setProps={mockSetProps} />);
  const instance = component.getInstance();
  act(() => {
    instance.setState({
      selectedText: 'Hello',
      selectedRange: { startOffset: 0, endOffset: 5 }
    });
  });
  act(() => {
    instance.handleLabelSelection('PERSON');
  });
  expect(mockSetProps).toHaveBeenCalledWith({
    entities: expect.arrayContaining([
      expect.objectContaining({
        text: 'Hello',
        label: 'PERSON',
        start: 0,
        end: 5
      })
    ])
  });
});

test('double click removes entity', () => {
  const mockSetProps = jest.fn();
  const entities = [{ id: 1, text: 'Hello', label: 'PERSON', start: 0, end: 5 }];
  const component = renderer.create(
    <NERLabeler text="Hello world" entities={entities} setProps={mockSetProps} />
  );
  const span = component.root.findByProps({ className: 'ner-entity ner-person' });
  act(() => span.props.onDoubleClick({ stopPropagation: () => {} }));
  expect(mockSetProps).toHaveBeenCalledWith({ entities: [] });
});
